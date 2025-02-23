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
    teachMode: boolean
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
        const endpoint = teachMode ? 'teach-ham-sandwich-viz' : 'ham-sandwich-viz';

        const result = await fetchData(endpoint, 'POST', {
            redPoints: redData.map((point) => [point.x, point.y]),
            bluePoints: blueData.map((point) => [point.x, point.y]),
        });

        // Push steps to stepsTaken dynamically
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
            setFinalCut({
                slope: result.slope,
                intercept: result['y_intercept'],
            });
        }

    } catch (error) {
        setHasError(true);
    } finally {
        // Clear the timeout once the function finishes, and set the flag to false
        clearTimeout(timeout);
        setIsCalculating(false);
    }
};
