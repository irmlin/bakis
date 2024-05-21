// porp-types is a library for typechecking of props
import PropTypes from "prop-types";

// react-chartjs-2 components
import { Line } from "react-chartjs-2";
import annotationPlugin from 'chartjs-plugin-annotation';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
    Filler
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
    Filler,
    annotationPlugin
);

function StreamStatusChart({ color, title, description, modelScores, chart, size, threshold }) {

    color ??= "info";
    description ??= "";
    chart ??= {
        labels: [],
        datasets: {
            label: "Predictions",
            data: [],
        },
    };

    const { initialData, options } = configs(threshold);
    const [data, setData] = useState(initialData);

    useEffect(() => {
        // const labels = data.labels;
        // const datasets = data.datasets;
        const labels = data?.labels ?? [];
        const datasets = data?.datasets ?? [];

        if (labels.length < size) {
            labels.push('');
        }

        const crash_datapoints = datasets[0].data;
        // const nocrash_datapoints = datasets[1].data;

        if (crash_datapoints.length === size) {
            crash_datapoints.shift();
        }

        // if (nocrash_datapoints.length === size) {
            // nocrash_datapoints.shift();
        // }

        crash_datapoints.push(modelScores[0]);
        // nocrash_datapoints.push(modelScores[1]);

        setData({
            ...labels,
            ...datasets
        });
        setData(data);
    }, [modelScores]);

    return (
        <MDBox>
            <MDBox
                variant="gradient"
                bgColor={color}
                borderRadius="lg"
                coloredShadow={color}
                // py={2}
                // pr={0.5}
                // mt={-5}
                height="10rem"
            >
                <Line data={data} options={options}/>
            </MDBox>
        </MDBox>
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