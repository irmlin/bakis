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

function StreamStatusChart({ color, title, description, modelScores, chart, historySecs }) {

    color ??= "info";
    description ??= "";
    chart ??= {
        labels: [],
        datasets: {
            label: "Predictions",
            data: [],
        },
    };

    const { initialData, options } = configs(
        chart?.labels || [],
        chart?.datasets || {}
    );

    const [data, setData] = useState(initialData);

    useEffect(() => {
        // const labels = data.labels;
        // const datasets = data.datasets;
        const labels = data?.labels ?? [];
        const datasets = data?.datasets ?? [];

        const crash_datapoints = data?.datasets.at(0)?.data;
        if (crash_datapoints === undefined || crash_datapoints === null) {
            return;
        }

        const nocrash_datapoints = data?.datasets.at(1)?.data;
        if (nocrash_datapoints === undefined || nocrash_datapoints === null) {
            return;
        }

        if (labels.length < historySecs) {
            labels.push('');
        }

        if (crash_datapoints.length === historySecs) {
            crash_datapoints.shift();
        }

        if (nocrash_datapoints.length === historySecs) {
            nocrash_datapoints.shift();
        }

        crash_datapoints.push(modelScores[0]);
        nocrash_datapoints.push(modelScores[1]);

        setData({
            ...labels,
            ...datasets
        });
        setData(data);
    }, [modelScores]);

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
                    data && (
                        <Line data={data} options={options}/>
                    )
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
};

export default StreamStatusChart;