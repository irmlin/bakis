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
// import Fade from "@mui/material/Fade";

// Material Dashboard 2 React base styles
import colors from "Assets/theme-dark/base/colors";
import breakpoints from "Assets/theme-dark/base/breakpoints";
import typography from "Assets/theme-dark/base/typography";
import boxShadows from "Assets/theme-dark/base/boxShadows";
import borders from "Assets/theme-dark/base/borders";
import globals from "Assets/theme-dark/base/globals";

// Material Dashboard 2 React helper functions
import boxShadow from "Assets/theme-dark/functions/boxShadow";
import hexToRgb from "Assets/theme-dark/functions/hexToRgb";
import linearGradient from "Assets/theme-dark/functions/linearGradient";
import pxToRem from "Assets/theme-dark/functions/pxToRem";
import rgba from "Assets/theme-dark/functions/rgba";

// Material Dashboard 2 React components base styles for @mui material components
import sidenav from "Assets/theme-dark/components/sidenav";
import list from "Assets/theme-dark/components/list";
import listItem from "Assets/theme-dark/components/list/listItem";
import listItemText from "Assets/theme-dark/components/list/listItemText";
import card from "Assets/theme-dark/components/card";
import cardMedia from "Assets/theme-dark/components/card/cardMedia";
import cardContent from "Assets/theme-dark/components/card/cardContent";
import button from "Assets/theme-dark/components/button";
import iconButton from "Assets/theme-dark/components/iconButton";
import input from "Assets/theme-dark/components/form/input";
import inputLabel from "Assets/theme-dark/components/form/inputLabel";
import inputOutlined from "Assets/theme-dark/components/form/inputOutlined";
import textField from "Assets/theme-dark/components/form/textField";
import menu from "Assets/theme-dark/components/menu";
import menuItem from "Assets/theme-dark/components/menu/menuItem";
import switchButton from "Assets/theme-dark/components/form/switchButton";
import divider from "Assets/theme-dark/components/divider";
import tableContainer from "Assets/theme-dark/components/table/tableContainer";
import tableHead from "Assets/theme-dark/components/table/tableHead";
import tableCell from "Assets/theme-dark/components/table/tableCell";
import linearProgress from "Assets/theme-dark/components/linearProgress";
import breadcrumbs from "Assets/theme-dark/components/breadcrumbs";
import slider from "Assets/theme-dark/components/slider";
import avatar from "Assets/theme-dark/components/avatar";
import tooltip from "Assets/theme-dark/components/tooltip";
import appBar from "Assets/theme-dark/components/appBar";
import tabs from "Assets/theme-dark/components/tabs";
import tab from "Assets/theme-dark/components/tabs/tab";
import stepper from "Assets/theme-dark/components/stepper";
import step from "Assets/theme-dark/components/stepper/step";
import stepConnector from "Assets/theme-dark/components/stepper/stepConnector";
import stepLabel from "Assets/theme-dark/components/stepper/stepLabel";
import stepIcon from "Assets/theme-dark/components/stepper/stepIcon";
import select from "Assets/theme-dark/components/form/select";
import formControlLabel from "Assets/theme-dark/components/form/formControlLabel";
import formLabel from "Assets/theme-dark/components/form/formLabel";
import checkbox from "Assets/theme-dark/components/form/checkbox";
import radio from "Assets/theme-dark/components/form/radio";
import autocomplete from "Assets/theme-dark/components/form/autocomplete";
import container from "Assets/theme-dark/components/container";
import popover from "Assets/theme-dark/components/popover";
import buttonBase from "Assets/theme-dark/components/buttonBase";
import icon from "Assets/theme-dark/components/icon";
import svgIcon from "Assets/theme-dark/components/svgIcon";
import link from "Assets/theme-dark/components/link";
import dialog from "Assets/theme-dark/components/dialog";
import dialogTitle from "Assets/theme-dark/components/dialog/dialogTitle";
import dialogContent from "Assets/theme-dark/components/dialog/dialogContent";
import dialogContentText from "Assets/theme-dark/components/dialog/dialogContentText";
import dialogActions from "Assets/theme-dark/components/dialog/dialogActions";

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
    MuiMenuItem: { ...menuItem },
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
    MuiSelect: { ...select },
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
