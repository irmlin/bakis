import base64
import os
from typing import Tuple, List, Type

import cv2
from fastapi import HTTPException
from pydantic_core._pydantic_core import ValidationError
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Paragraph, Spacer
from sqlalchemy import or_
from sqlalchemy.orm import Session
from sqlalchemy import desc

from ..models import Accident, Video
from ..models.enums import accident_type_str_map
from ..models.validation_models import DateRangeParams
from ..utilities import generate_file_path


class AccidentService:

    def __init__(self):
        pass

    def get_accident_by_id(self, db: Session, accident_id: int):
        return db.query(Accident).filter(Accident.id == accident_id).first()


    def get_filtered_accidents(self, db: Session, datetime_from: str = None, datetime_to: str = None,
                               source_ids: List[int] = None, skip: int = 0, limit: int = 10):
        try:
            datetime_params: DateRangeParams = DateRangeParams(datetime_from=datetime_from, datetime_to=datetime_to)
        except ValidationError:
            raise HTTPException(status_code=422, detail=f'Invalid datetime received! Expected: (YYYY:mm:DD HH:MM:SS).')
        print(datetime_params)
        db_accidents_query = self.__get_filtered_accidents_query(db=db, datetime_params=datetime_params,
                                                                 source_ids=source_ids)
        db_accidents = db_accidents_query.order_by(desc(Accident.id)).offset(skip).limit(limit).all()

        return db_accidents

    def get_sources_by_ids(self, db: Session, ids: List[int]):
        if ids is None:
            return None
        query = db.query(Video)
        source_id_conditions = [Video.id == source_id for source_id in ids]
        query = query.filter(or_(*source_id_conditions))
        return query.all()

    def __get_filtered_accidents_query(self, db: Session, datetime_params: DateRangeParams, source_ids: List[int]):
        query = db.query(Accident)
        if datetime_params.datetime_from is not None:
            print('here1', type(datetime_params.datetime_from))
            query = query.filter(Accident.created_at >= datetime_params.datetime_from)
        if datetime_params.datetime_to is not None:
            print('here2', datetime_params.datetime_to)
            query = query.filter(Accident.created_at <= datetime_params.datetime_to)
        if source_ids:
            print('here3')
            source_id_conditions = [Accident.video_id == video_id for video_id in source_ids]
            query = query.filter(or_(*source_id_conditions))
        return query

    def get_accident_image(self, accident_id: int, db: Session):
        db_accident = self.get_accident_by_id(db, accident_id)
        if db_accident is None:
            raise HTTPException(status_code=404, detail=f'Accident with id {accident_id} not found.')
        if not self.__file_exists(db_accident.image_path):
            raise HTTPException(status_code=404, detail=f'No image found for accident with id {accident_id}.')

        with open(db_accident.image_path, 'rb') as f:
            base64image = base64.b64encode(f.read())
        return base64image

    def download_accident_video(self, accident_id: int, db: Session) -> Tuple[str, str]:
        db_accident: Accident = self.get_accident_by_id(db, accident_id)
        if db_accident is None:
            raise HTTPException(status_code=404, detail=f'Accident with id {accident_id} not found.')
        if not self.__file_exists(db_accident.video_path):
            raise HTTPException(status_code=404, detail=f'No video found for accident with id {accident_id}.')

        ext = os.path.splitext(db_accident.video_path)[1]
        return (db_accident.video_path,
                f'{db_accident.created_at}_from_{db_accident.video.title}_type_{db_accident.type}{ext}')

    def download_report_pdf(self, db: Session, datetime_from: str = None, datetime_to: str = None,
                            video_ids: List[int] = None) -> Tuple[str, str]:
        try:
            datetime_params: DateRangeParams = DateRangeParams(datetime_from=datetime_from, datetime_to=datetime_to)
        except ValidationError:
            raise HTTPException(status_code=422, detail=f'Invalid datetime received! Expected: (YYYY:mm:DD HH:MM:SS).')
        db_accidents = self.__get_filtered_accidents(db=db, datetime_params=datetime_params, video_ids=video_ids)
        if db_accidents is None or len(db_accidents) == 0:
            raise HTTPException(status_code=404, detail=f'No accidents found with provided filter:'
                                                        f' from {datetime_from}; to {datetime_to}; source ids: {video_ids}.')

        sources = self.get_sources_by_ids(db=db, ids=video_ids)
        return self.__build_pdf(accidents=db_accidents, datetime_from=datetime_from,
                                datetime_to=datetime_to, sources=sources)

    def __build_pdf(self, accidents: List[Type[Accident]], datetime_from: str, datetime_to: str,
                    sources: List[Type[Video]], max_img_width=200, columns=None) -> Tuple[str, str]:
        if columns is None:
            columns = ["Detected At", "Camera/Video", "Accident Type", "Model Score", "Image"]
        pdf_path = generate_file_path('.pdf')

        doc = SimpleDocTemplate(pdf_path, pagesize=A4)

        data = [columns]
        for accident in accidents:
            img = cv2.imread(str(accident.image_path))
            h, w, _ = img.shape
            ratio = 1
            if w > max_img_width:
                ratio = max_img_width / w
            pdf_img_h, pdf_img_w = h * ratio, w * ratio
            data.append([accident.created_at, accident.video.title,
                         accident_type_str_map[accident.type], str(accident.score),
                         Image(accident.image_path, width=pdf_img_w, height=pdf_img_h)])

        table = Table(data)
        style = TableStyle([
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (1, -1), 'LEFT'),
            ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 0.2, colors.black)
        ])

        table.setStyle(style)
        title = Paragraph("Detected Accidents Export",
                          style=ParagraphStyle(name="TitleStyle", fontSize=20, textColor="black", bold=True,
                                               italic=True, alignment=TA_CENTER))
        if datetime_from is None and datetime_to is not None:
            date_info_str = f'to {datetime_to}'
            pdf_name = f'export_to_{datetime_to}.pdf'
        elif datetime_from is not None and datetime_to is None:
            date_info_str = f'from {datetime_from}'
            pdf_name = f'export_from_{datetime_from}.pdf'
        elif datetime_from is None and datetime_to is None:
            date_info_str = f'all time'
            pdf_name = f'export_all_time.pdf'
        else:
            date_info_str = f'from {datetime_from} to {datetime_to}'
            pdf_name = f'export_from_{datetime_from}_to_{datetime_to}.pdf'
        date_info = Paragraph(f"Date interval: {date_info_str}",
                              style=ParagraphStyle(name="DateInfoStyle", fontSize=12, textColor="black", bold=True,
                                                   italic=True, alignment=TA_CENTER))
        if sources is None:
            sources_str = 'all'
        else:
            sources_titles = [str(source.title) for source in sources]
            sources_str = ', '.join(sources_titles)
        sources_info = Paragraph(f"Cameras/videos: {sources_str}",
                                 style=ParagraphStyle(name="DateInfoStyle", fontSize=12, textColor="black", bold=True,
                                                      italic=True, alignment=TA_CENTER))

        # Build the PDF document
        elements = [title, Spacer(1, 20), date_info, Spacer(1, 10),
                    sources_info, Spacer(1, 40), table]
        doc.build(elements)

        return pdf_path, pdf_name

    # def show_accident_video(self, accident_id: int, db: Session) -> Tuple[str, str]:
    #     db_accident: Accident = self.get_accident_by_id(db, accident_id)
    #     if db_accident is None:
    #         raise HTTPException(status_code=404, detail=f'Accident with id {accident_id} not found.')
    #     if not self.__file_exists(db_accident.video_path):
    #         raise HTTPException(status_code=404, detail=f'No video found for accident with id {accident_id}.')
    #
    #     ext = os.path.splitext(db_accident.video_path)[1]
    #     return (db_accident.video_path,
    #             f'{db_accident.created_at}_from_{db_accident.video.title}_type_{db_accident.type}{ext}')

    # TODO: move to utils
    def __file_exists(self, file_path: str):
        return os.path.exists(file_path)

    def __delete_file(self, file_path: str):
        if self.__file_exists(file_path):
            os.remove(file_path)
