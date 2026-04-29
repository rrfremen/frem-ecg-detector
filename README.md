# frem-ecg-detector

A Python-based ECG Heartbeat detection application with real-time signal
processing and visualization.

The system implements a streaming processing pipeline for low-latency ECG
analysis, including bandpass filtering, feature extraction, and beat detection
using a look-back mechanism. Data is processed sample-by-sample from the
MIT-BIH arrhythmia dataset to simulate real-time acquisition.

The architecture is designed for real-time operation, addressing challenges
such as buffering, synchronization, and signal alignment using shared memory 
and versioned communication between processing (IPC) and visualization.

The application includes a Qt-based GUI for live signal visualization and
analysis. 

This project was developed from a strong interest in ECG systems
and software engineering, with a focus on building robust real-time
processing pipelines. It reflects my approach to designing systems from 
first principles, emphasizing clarity, correctness, and control
over the implementation.
