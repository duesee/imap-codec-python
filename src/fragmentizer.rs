use imap_codec::fragmentizer::{FragmentInfo, Fragmentizer, LineEnding, LiteralAnnouncement};
use pyo3::{exceptions::PyTypeError, prelude::*, types::PyBytes};

use crate::encoded::PyLiteralMode;

/// Python class representing a line ending
#[derive(Debug, Clone, Copy, PartialEq)]
#[pyclass(name = "LineEnding", eq)]
pub(crate) enum PyLineEnding {
    Lf,
    CrLf,
}

impl std::fmt::Display for PyLineEnding {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            PyLineEnding::Lf => f.write_str("LineEnding.Lf"),
            PyLineEnding::CrLf => f.write_str("LineEnding.CrLf"),
        }
    }
}

impl From<LineEnding> for PyLineEnding {
    fn from(value: LineEnding) -> Self {
        match value {
            LineEnding::Lf => Self::Lf,
            LineEnding::CrLf => Self::CrLf,
        }
    }
}

impl From<PyLineEnding> for LineEnding {
    fn from(value: PyLineEnding) -> Self {
        match value {
            PyLineEnding::Lf => Self::Lf,
            PyLineEnding::CrLf => Self::CrLf,
        }
    }
}

/// Python class representing a literal announcement
#[derive(Debug, Clone, Copy, PartialEq)]
#[pyclass(name = "LiteralAnnouncement", eq)]
pub(crate) struct PyLiteralAnnouncement {
    mode: PyLiteralMode,
    length: u32,
}

impl From<LiteralAnnouncement> for PyLiteralAnnouncement {
    fn from(value: LiteralAnnouncement) -> Self {
        Self {
            mode: value.mode.into(),
            length: value.length,
        }
    }
}

impl From<PyLiteralAnnouncement> for LiteralAnnouncement {
    fn from(value: PyLiteralAnnouncement) -> Self {
        Self {
            mode: value.mode.into(),
            length: value.length,
        }
    }
}

#[pymethods]
impl PyLiteralAnnouncement {
    /// Create a new literal announcement
    #[new]
    pub(crate) fn new(mode: PyLiteralMode, length: u32) -> Self {
        Self { mode, length }
    }

    /// Retrieve the mode of the announced literal
    #[getter]
    pub(crate) fn mode(&self) -> PyLiteralMode {
        self.mode
    }

    /// Retrieve the length of the announced literal
    #[getter]
    pub(crate) fn length(&self) -> u32 {
        self.length
    }
}

/// Python class describing a line fragment detected by the fragmentizer
#[derive(Debug, Clone, Copy, PartialEq)]
#[pyclass(name = "LineFragmentInfo", eq)]
pub(crate) struct PyLineFragmentInfo {
    start: usize,
    end: usize,
    announcement: Option<PyLiteralAnnouncement>,
    ending: PyLineEnding,
}

impl From<PyLineFragmentInfo> for FragmentInfo {
    fn from(value: PyLineFragmentInfo) -> Self {
        Self::Line {
            start: value.start,
            end: value.end,
            announcement: value.announcement.map(PyLiteralAnnouncement::into),
            ending: value.ending.into(),
        }
    }
}

#[pymethods]
impl PyLineFragmentInfo {
    /// Create a new line fragment
    #[new]
    #[pyo3(signature = (start, end, announcement=None, ending=PyLineEnding::CrLf))]
    pub(crate) fn new(
        start: usize,
        end: usize,
        announcement: Option<PyLiteralAnnouncement>,
        ending: PyLineEnding,
    ) -> Self {
        Self {
            start,
            end,
            announcement,
            ending,
        }
    }

    /// Retrieve the start index of the detected line fragment
    #[getter]
    pub(crate) fn start(&self) -> usize {
        self.start
    }

    /// Retrieve the end index of the detected line fragment
    #[getter]
    pub(crate) fn end(&self) -> usize {
        self.end
    }

    /// Retrieve the literal announcement of the detected line fragment
    #[getter]
    pub(crate) fn announcement(&self) -> Option<PyLiteralAnnouncement> {
        self.announcement
    }

    /// Retrieve the line ending of the detected line fragment
    #[getter]
    pub(crate) fn ending(&self) -> PyLineEnding {
        self.ending
    }
}

/// Python class describing a literal fragment detected by the fragmentizer
#[derive(Debug, Clone, Copy, PartialEq)]
#[pyclass(name = "LiteralFragmentInfo", eq)]
pub(crate) struct PyLiteralFragmentInfo {
    start: usize,
    end: usize,
}

impl From<PyLiteralFragmentInfo> for FragmentInfo {
    fn from(value: PyLiteralFragmentInfo) -> Self {
        Self::Literal {
            start: value.start,
            end: value.end,
        }
    }
}

#[pymethods]
impl PyLiteralFragmentInfo {
    /// Create a new literal fragment
    #[new]
    pub(crate) fn new(start: usize, end: usize) -> Self {
        Self { start, end }
    }

    /// Retrieve the start index of the detected literal fragment
    #[getter]
    pub(crate) fn start(&self) -> usize {
        self.start
    }

    /// Retrieve the end index of the detected literal fragment
    #[getter]
    pub(crate) fn end(&self) -> usize {
        self.end
    }
}

/// Python class representing a fragmentizer
#[derive(Debug, Clone)]
#[pyclass(name = "Fragmentizer")]
pub(crate) struct PyFragmentizer(Fragmentizer);

#[pymethods]
impl PyFragmentizer {
    /// Create a new fragmentizer
    #[new]
    #[pyo3(signature = (*, max_message_size=None))]
    pub(crate) fn new(max_message_size: Option<u32>) -> Self {
        Self(
            max_message_size.map_or_else(Fragmentizer::without_max_message_size, Fragmentizer::new),
        )
    }

    /// Progress the fragmentizer and return the next detected fragment
    pub(crate) fn progress(&mut self, py: Python) -> PyResult<Option<PyObject>> {
        let Some(fragment_info) = self.0.progress() else {
            return Ok(None);
        };

        let frament_info = match fragment_info {
            FragmentInfo::Line {
                start,
                end,
                announcement,
                ending,
            } => {
                let line_fragment_info = PyLineFragmentInfo::new(
                    start,
                    end,
                    announcement.map(LiteralAnnouncement::into),
                    ending.into(),
                );
                Bound::new(py, line_fragment_info)?.to_object(py)
            }
            FragmentInfo::Literal { start, end } => {
                let literal_fragment_info = PyLiteralFragmentInfo::new(start, end);
                Bound::new(py, literal_fragment_info)?.to_object(py)
            }
        };

        Ok(Some(frament_info))
    }

    /// Enqueue more bytes to the fragmentizer
    pub(crate) fn enqueue_bytes(&mut self, bytes: Bound<PyBytes>) {
        self.0.enqueue_bytes(bytes.as_bytes())
    }

    /// Retrieve the bytes for the given fragment
    pub(crate) fn fragment_bytes<'a>(
        slf: PyRef<'a, Self>,
        fragment_info: &Bound<PyAny>,
    ) -> PyResult<Bound<'a, PyBytes>> {
        let fragment_info: FragmentInfo =
            if let Ok(info) = fragment_info.downcast::<PyLineFragmentInfo>() {
                (*info.borrow()).into()
            } else if let Ok(info) = fragment_info.downcast::<PyLiteralFragmentInfo>() {
                (*info.borrow()).into()
            } else {
                return Err(PyErr::new::<PyTypeError, _>(
                    "fragment_info must be either of type LineFragmentInfo or LiteralFragmentInfo",
                ));
            };

        let bytes = slf.0.fragment_bytes(fragment_info);
        Ok(PyBytes::new_bound(slf.py(), bytes))
    }

    /// Return if the current message is completely processed
    pub(crate) fn is_message_complete(&self) -> bool {
        self.0.is_message_complete()
    }

    /// Retrive the bytes of the current message
    pub(crate) fn message_bytes(slf: PyRef<Self>) -> Bound<PyBytes> {
        let bytes = slf.0.message_bytes();
        PyBytes::new_bound(slf.py(), bytes)
    }

    // Return if the current message exceeded the max message size
    pub(crate) fn is_max_message_size_exceeded(&self) -> bool {
        self.0.is_max_message_size_exceeded()
    }

    // Skip the current message and start the next message immediately
    pub(crate) fn skip_message(&mut self) {
        self.0.skip_message()
    }

    // pub(crate) fn decode_tag(slf: PyRef<'_, Self>) -> Option<PyTag> {
    //     todo!()
    // }

    // pub(crate) fn decode_greeting(slf: PyRef<'_, Self>) -> PyResult<PyGreeting> {
    //     todo!()
    // }

    // pub(crate) fn decode_command(slf: PyRef<'_, Self>) -> PyResult<PyCommand> {
    //     todo!()
    // }

    // pub(crate) fn decode_authenticate_data(slf: PyRef<'_, Self>) -> PyResult<PyAuthenticateData> {
    //     todo!()
    // }

    // pub(crate) fn decode_response(slf: PyRef<'_, Self>) -> PyResult<PyResponse> {
    //     todo!()
    // }

    // pub(crate) fn decode_idle_done(slf: PyRef<'_, Self>) -> PyResult<PyIdleDone> {
    //     todo!()
    // }
}
