/**
=========================================================
* Material Dashboard 2 React - v2.2.0
=========================================================

* Product Page: https://www.creative-tim.com/product/material-dashboard-react
* Copyright 2023 Creative Tim (https://www.creative-tim.com)

Coded by www.creative-tim.com

 =========================================================

* The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
*/

// @mui material components
import { createTheme } from "@mui/material/styles";

// Material Dashboard 2 React base styles
import colors from "Assets/theme/base/colors";
import breakpoints from "Assets/theme/base/breakpoints";
import typography from "Assets/theme/base/typography";
import boxShadows from "Assets/theme/base/boxShadows";
import borders from "Assets/theme/base/borders";
import globals from "Assets/theme/base/globals";

// Material Dashboard 2 React helper functions
import boxShadow from "Assets/theme/functions/boxShadow";
import hexToRgb from "Assets/theme/functions/hexToRgb";
import linearGradient from "Assets/theme/functions/linearGradient";
import pxToRem from "Assets/theme/functions/pxToRem";
import rgba from "Assets/theme/functions/rgba";

// Material Dashboard 2 React components base styles for @mui material components
import sidenav from "Assets/theme/components/sidenav";
import list from "Assets/theme/components/list";
import listItem from "Assets/theme/components/list/listItem";
import listItemText from "Assets/theme/components/list/listItemText";
import card from "Assets/theme/components/card";
import cardMedia from "Assets/theme/components/card/cardMedia";
import cardContent from "Assets/theme/components/card/cardContent";
import button from "Assets/theme/components/button";
import iconButton from "Assets/theme/components/iconButton";
import input from "Assets/theme/components/form/input";
import inputLabel from "Assets/theme/components/form/inputLabel";
import inputOutlined from "Assets/theme/components/form/inputOutlined";
import textField from "Assets/theme/components/form/textField";
import menu from "Assets/theme/components/menu";
import menuItem from "Assets/theme/components/menu/menuItem";
import switchButton from "Assets/theme/components/form/switchButton";
import divider from "Assets/theme/components/divider";
import tableContainer from "Assets/theme/components/table/tableContainer";
import tableHead from "Assets/theme/components/table/tableHead";
import tableCell from "Assets/theme/components/table/tableCell";
import linearProgress from "Assets/theme/components/linearProgress";
import breadcrumbs from "Assets/theme/components/breadcrumbs";
import slider from "Assets/theme/components/slider";
import avatar from "Assets/theme/components/avatar";
import tooltip from "Assets/theme/components/tooltip";
import appBar from "Assets/theme/components/appBar";
import tabs from "Assets/theme/components/tabs";
import tab from "Assets/theme/components/tabs/tab";
import stepper from "Assets/theme/components/stepper";
import step from "Assets/theme/components/stepper/step";
import stepConnector from "Assets/theme/components/stepper/stepConnector";
import stepLabel from "Assets/theme/components/stepper/stepLabel";
import stepIcon from "Assets/theme/components/stepper/stepIcon";
import select from "Assets/theme/components/form/select";
import formControlLabel from "Assets/theme/components/form/formControlLabel";
import formLabel from "Assets/theme/components/form/formLabel";
import checkbox from "Assets/theme/components/form/checkbox";
import radio from "Assets/theme/components/form/radio";
import autocomplete from "Assets/theme/components/form/autocomplete";
import container from "Assets/theme/components/container";
import popover from "Assets/theme/components/popover";
import buttonBase from "Assets/theme/components/buttonBase";
import icon from "Assets/theme/components/icon";
import svgIcon from "Assets/theme/components/svgIcon";
import link from "Assets/theme/components/link";
import dialog from "Assets/theme/components/dialog";
import dialogTitle from "Assets/theme/components/dialog/dialogTitle";
import dialogContent from "Assets/theme/components/dialog/dialogContent";
import dialogContentText from "Assets/theme/components/dialog/dialogContentText";
import dialogActions from "Assets/theme/components/dialog/dialogActions";

export default createTheme({
  breakpoints: { ...breakpoints },
  palette: { ...colors },
  typography: { ...typography },
  boxShadows: { ...boxShadows },
  borders: { ...borders },
  functions: {
    boxShadow,
    hexToRgb,
    linearGradient,
    pxToRem,
    rgba,
  },

  components: {
    MuiCssBaseline: {
      styleOverrides: {
        ...globals,
        ...container,
      },
    },
    MuiDrawer: { ...sidenav },
    MuiList: { ...list },
    MuiListItem: { ...listItem },
    MuiListItemText: { ...listItemText },
    MuiCard: { ...card },
    MuiCardMedia: { ...cardMedia },
    MuiCardContent: { ...cardContent },
    MuiButton: { ...button },
    MuiIconButton: { ...iconButton },
    MuiInput: { ...input },
    MuiInputLabel: { ...inputLabel },
    MuiOutlinedInput: { ...inputOutlined },
    MuiTextField: { ...textField },
    MuiMenu: { ...menu },
    // MuiMenuItem: { ...menuItem },
    MuiSwitch: { ...switchButton },
    MuiDivider: { ...divider },
    MuiTableContainer: { ...tableContainer },
    MuiTableHead: { ...tableHead },
    MuiTableCell: { ...tableCell },
    MuiLinearProgress: { ...linearProgress },
    MuiBreadcrumbs: { ...breadcrumbs },
    MuiSlider: { ...slider },
    MuiAvatar: { ...avatar },
    MuiTooltip: { ...tooltip },
    MuiAppBar: { ...appBar },
    MuiTabs: { ...tabs },
    MuiTab: { ...tab },
    MuiStepper: { ...stepper },
    MuiStep: { ...step },
    MuiStepConnector: { ...stepConnector },
    MuiStepLabel: { ...stepLabel },
    MuiStepIcon: { ...stepIcon },
    // MuiSelect: { ...select },
    MuiFormControlLabel: { ...formControlLabel },
    MuiFormLabel: { ...formLabel },
    MuiCheckbox: { ...checkbox },
    MuiRadio: { ...radio },
    MuiAutocomplete: { ...autocomplete },
    MuiPopover: { ...popover },
    MuiButtonBase: { ...buttonBase },
    MuiIcon: { ...icon },
    MuiSvgIcon: { ...svgIcon },
    MuiLink: { ...link },
    MuiDialog: { ...dialog },
    MuiDialogTitle: { ...dialogTitle },
    MuiDialogContent: { ...dialogContent },
    MuiDialogContentText: { ...dialogContentText },
    MuiDialogActions: { ...dialogActions },
  },
});
