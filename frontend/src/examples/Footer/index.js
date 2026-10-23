import Icon from "@mui/material/Icon";
import MDBox from "components/MDBox";
import typography from "assets/theme/base/typography";

function Footer() {
  const { size } = typography;

  return (
    <MDBox
      width="100%"
      display="flex"
      justifyContent="center"
      alignItems="center"
      px={1.5}
      py={2}
      color="text"
      fontSize={size.sm}
    >
      &copy; EduForge 2025, hecho con
      <MDBox fontSize={size.md} color="text" mb={-0.5} mx={0.25}>
        <Icon color="inherit" fontSize="inherit">
          favorite
        </Icon>
      </MDBox>
      para la educación y desarrollo académico
    </MDBox>
  );
}

export default Footer;
