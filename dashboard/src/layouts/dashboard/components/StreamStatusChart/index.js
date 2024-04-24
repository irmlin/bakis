// porp-types is a library for typechecking of props
import PropTypes from "prop-types";

// react-chartjs-2 components
import { Line } from "react-chartjs-2";
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
    Filler,
} from "chart.js";

// @mui material components
import Card from "@mui/material/Card";

// Material Dashboard 2 React components
import MDBox from "Components/MDBox";
import MDTypography from "Components/MDTypography";

// ReportsLineChart configurations
import configs from "Examples/Charts/LineCharts/ReportsLineChart/configs";
import { useState, useEffect } from "react";

ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
    Filler
);

function StreamStatusChart({ color, title, description, chart, input }) {
    // create defaults
    color ??= "info";
    description ??= "";
    chart ??= {
        labels: [],
        datasets: {
            label: "Model output",
            data: [],
        },
    };

    const { data, options } = configs(
        chart?.labels || [],
        chart?.datasets || {}
    );

    // labels: ["Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    // datasets: {
    //     label: "Desktop apps",
    //     data: [50, 40, 300, 220, 500, 250, 400, 230, 500],
    // },

    useEffect(() => {
        if (!isFinite(input.crash)) {
            return;
        }

        if (!isFinite(input.noCrash)) {
            return;
        }

        const labels = data?.labels ?? [];
        const datapoints = data?.datasets.at(0)?.data;

        if (datapoints === undefined || datapoints === null) {
            return;
        }

        labels.push(input.noCrash);
        datapoints.push(input.crash);

        // make a copy of data, to make sure that detection cycle is invoked
        // addData({
        //     ...data,
        //     labels: [...data.labels],
        //     datasets: [
        //         {
        //             data: [...datapoints],
        //         }
        //     ],
        // });
        addData(data);
    }, [input]);

    const [statefulData, addData] = useState(data);

    return (
        <Card sx={{ height: "100%" }}>
            <MDBox padding="1rem">
                <MDBox
                    variant="gradient"
                    bgColor={color}
                    borderRadius="lg"
                    coloredShadow={color}
                    py={2}
                    pr={0.5}
                    mt={-5}
                    height="12.5rem"
                >
                    <Line data={statefulData} options={options} redraw />
                </MDBox>
                <MDBox pt={3} pb={1} px={1}>
                    <MDTypography variant="h6" textTransform="capitalize">
                        {title}
                    </MDTypography>
                    <MDTypography
                        component="div"
                        variant="button"
                        color="text"
                        fontWeight="light"
                    >
                        {description}
                    </MDTypography>
                </MDBox>
            </MDBox>
        </Card>
    );
}

// Typechecking props for the ReportsLineChart
StreamStatusChart.propTypes = {
    color: PropTypes.oneOf([
        "primary",
        "secondary",
        "info",
        "success",
        "warning",
        "error",
        "dark",
    ]),
    title: PropTypes.string.isRequired,
    description: PropTypes.oneOfType([PropTypes.string, PropTypes.node]),
    chart: PropTypes.objectOf(
        PropTypes.oneOfType([PropTypes.array, PropTypes.object])
    ).isRequired,
};

export default StreamStatusChart;
