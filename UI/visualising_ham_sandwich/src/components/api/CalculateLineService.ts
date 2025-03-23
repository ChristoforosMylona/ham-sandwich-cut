import { SetStateAction, Dispatch } from 'react';
import { Point } from '../ReachChartJs/Types/Step';
import { fetchData } from './api';

export const calculateLine = async (
    redData: Point[],
    blueData: Point[],
    setIsCalculating: Dispatch<SetStateAction<boolean>>,
    setHasError: Dispatch<SetStateAction<boolean>>,
    setStepsTaken: Dispatch<SetStateAction<any[]>>,
    setFinalCut: Dispatch<SetStateAction<any>>,
    teachMode: boolean,
    selectedEndpoint: string
) => {
    if (redData.length === 0 || blueData.length === 0) {
        return; // Exit early if either dataset is empty
    }

    // Set the calculating flag right at the start
    const timeout = setTimeout(() => {
        setIsCalculating(true); // Set to true if it's been more than 500ms
    }, 500);

    setHasError(false);

    try {
        const endpoint =
            selectedEndpoint === 'default'
                ? teachMode
                    ? 'teach-ham-sandwich-viz'
                    : 'ham-sandwich-viz'
                : selectedEndpoint;


        // Fetch data from the backend API
        const result = await fetchData(endpoint, 'POST', {
            redPoints: redData.map((point) => [point.x, point.y]),
            bluePoints: blueData.map((point) => [point.x, point.y]),
        });

        // Handle the result based on teach mode
        if (teachMode) {
            setStepsTaken([
                {
                    id: 0,
                    type: 'initial_graph',
                    description: 'Initial Graph',
                    data: {},
                },
                ...result.stepsTaken,
            ]);
        } else {
            const { is_vertical, slope, y_intercept, x_intercept } = result;

            // For non-vertical lines, store slope and intercept
            if (is_vertical) {
                setFinalCut({
                    slope: null, // No slope for vertical lines
                    intercept: null, // No intercept for vertical lines
                    x_intercept: x_intercept, // x_intercept for vertical line
                    is_vertical: true, // Mark it as vertical
                });

                // Run only in development mode
                if (import.meta.env.MODE === 'development') {
                    // Check for correct splitting in vertical case
                    const leftOfLine = redData.filter(point => point.x < x_intercept).length;
                    const rightOfLine = redData.filter(point => point.x > x_intercept).length;
                    const blueLeftOfLine = blueData.filter(point => point.x < x_intercept).length;
                    const blueRightOfLine = blueData.filter(point => point.x > x_intercept).length;

                    if (
                        Math.abs(leftOfLine - rightOfLine) > redData.length / 2 ||
                        Math.abs(blueLeftOfLine - blueRightOfLine) > blueData.length / 2
                    ) {
                        console.warn('The vertical cut does not split the points in half correctly.');
                    } else {
                        console.log('The vertical cut does split the points in half correctly!');
                    }
                }
            } else {
                setFinalCut({
                    slope: slope, // Store slope for non-vertical lines
                    intercept: y_intercept, // Store intercept for non-vertical lines
                    x_intercept: null, // No x_intercept for non-vertical lines
                    is_vertical: false, // Mark it as non-vertical
                });

                // Run only in development mode
                if (import.meta.env.MODE === 'development') {
                    // Check for correct splitting in non-vertical case
                    const redAboveLine = redData.filter(point => point.y > slope * point.x + y_intercept).length;
                    const redBelowLine = redData.filter(point => point.y < slope * point.x + y_intercept).length;
                    const blueAboveLine = blueData.filter(point => point.y > slope * point.x + y_intercept).length;
                    const blueBelowLine = blueData.filter(point => point.y < slope * point.x + y_intercept).length;

                    // Check if the points are split correctly for both red and blue datasets
                    if (
                        Math.abs(redAboveLine - redBelowLine) > redData.length / 2 ||
                        Math.abs(blueAboveLine - blueBelowLine) > blueData.length / 2
                    ) {
                        console.warn('The non-vertical cut does not split the points in half correctly.');
                    } else {
                        console.log('The non-vertical cut does split the points in half correctly!');

                    }
                }
            }
        }
    } catch (error) {
        setHasError(true);
    } finally {
        // Clear the timeout once the function finishes, and set the flag to false
        clearTimeout(timeout);
        setIsCalculating(false);
    }
};
