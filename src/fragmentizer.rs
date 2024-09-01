use imap_codec::{
    decode::Decoder,
    fragmentizer::{self, FragmentInfo, Fragmentizer, LineEnding, LiteralAnnouncement},
    imap_types::ToStatic,
    AuthenticateDataCodec, CommandCodec, GreetingCodec, IdleDoneCodec, ResponseCodec,
};
use pyo3::{
    create_exception,
    exceptions::{PyException, PyTypeError},
    prelude::*,
    types::{PyBytes, PyString},
};
use serde::Serialize;

use crate::{
    encoded::PyLiteralMode, map_authenticate_data_decode_error, map_command_decode_error,
    map_greeting_decode_error, map_idle_done_decode_error, map_response_decode_error,
    PyAuthenticateData, PyCommand, PyGreeting, PyIdleDone, PyResponse,
};

// Create exception types for fragmentizer specific decode message errors
create_exception!(imap_codec, FragmentizerDecodeError, PyException);
create_exception!(
    imap_codec,
    FragmentizerDecodingRemainderError,
    FragmentizerDecodeError
);
create_exception!(
    imap_codec,
    FragmentizerMessageTooLongError,
    FragmentizerDecodeError
);
create_exception!(
    imap_codec,
    FragmentizerMessagePoisonedError,
    FragmentizerDecodeError
);

/// Python class representing a line ending
#[derive(Debug, Clone, Copy, PartialEq)]
#[pyclass(name = "LineEnding", eq)]
pub(crate) enum PyLineEnding {
    Lf,
    CrLf,
}

/// Only for local usage, `__str__` and `__repr__` for Python class `LineEnding` are generated
impl std::fmt::Display for PyLineEnding {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::Lf => f.write_str("LineEnding.Lf"),
            Self::CrLf => f.write_str("LineEnding.CrLf"),
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
    #[pyo3(signature = (mode, *, length))]
    fn new(mode: PyLiteralMode, length: u32) -> Self {
        Self { mode, length }
    }

    /// Retrieve the mode of the announced literal
    #[getter]
    fn mode(&self) -> PyLiteralMode {
        self.mode
    }

    /// Retrieve the length of the announced literal
    #[getter]
    fn length(&self) -> u32 {
        self.length
    }

    /// String representation of the literal announcement, e.g. `(LiteralMode.Sync, 42)`
    fn __str__(&self, _py: Python) -> String {
        format!("({}, {})", self.mode, self.length)
    }

    /// Printable representation of the literal announcement,
    /// e.g. `LiteralAnnouncement(LiteralMode.Sync, length=42)`
    fn __repr__(&self, _py: Python) -> String {
        format!("LiteralAnnouncement({}, length={})", self.mode, self.length)
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
    #[pyo3(signature = (*, start, end, announcement=None, ending=PyLineEnding::CrLf))]
    fn new(
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
    fn start(&self) -> usize {
        self.start
    }

    /// Retrieve the end index of the detected line fragment
    #[getter]
    fn end(&self) -> usize {
        self.end
    }

    /// Retrieve the literal announcement of the detected line fragment
    #[getter]
    fn announcement(&self) -> Option<PyLiteralAnnouncement> {
        self.announcement
    }

    /// Retrieve the line ending of the detected line fragment
    #[getter]
    fn ending(&self) -> PyLineEnding {
        self.ending
    }

    /// String representation of the line fragment info,
    /// e.g. `(17, 71, (LiteralMode.Sync, 42), LineEnding.Lf)`
    fn __str__(&self, py: Python) -> String {
        format!(
            "({}, {}, {}, {})",
            self.start,
            self.end,
            self.announcement
                .as_ref()
                .map_or_else(|| "None".to_string(), |a| a.__str__(py)),
            self.ending,
        )
    }

    /// Printable representation of the line fragment info,
    /// e.g. `LineFragmentInfo(start=17, end=71, announcement=LiteralAnnouncement(LiteralMode.Sync, 42), ending=LineEnding.Lf)`
    fn __repr__(&self, py: Python) -> String {
        format!(
            "LineFragmentInfo(start={}, end={}, announcement={}, ending={})",
            self.start,
            self.end,
            self.announcement
                .as_ref()
                .map_or_else(|| "None".to_string(), |a| a.__repr__(py)),
            self.ending,
        )
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
    #[pyo3(signature = (*, start, end))]
    fn new(start: usize, end: usize) -> Self {
        Self { start, end }
    }

    /// Retrieve the start index of the detected literal fragment
    #[getter]
    fn start(&self) -> usize {
        self.start
    }

    /// Retrieve the end index of the detected literal fragment
    #[getter]
    fn end(&self) -> usize {
        self.end
    }

    /// String representation of the literal fragment info, e.g. `(17, 71)`
    fn __str__(&self, _py: Python) -> String {
        format!("({}, {})", self.start, self.end)
    }

    /// Printable representation of the literal fragment info,
    /// e.g. `LiteralFragmentInfo(start=17, end=71)`
    fn __repr__(&self, _py: Python) -> String {
        format!(
            "LiteralFragmentInfo(start={}, end={})",
            self.start, self.end
        )
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
    #[pyo3(signature = (*, max_message_size))]
    fn new(max_message_size: Option<u32>) -> Self {
        Self(
            max_message_size.map_or_else(Fragmentizer::without_max_message_size, Fragmentizer::new),
        )
    }

    /// Progress the fragmentizer and return the next detected fragment
    fn progress(&mut self, py: Python) -> PyResult<Option<PyObject>> {
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
                Bound::new(py, line_fragment_info)?
                    .into_pyobject(py)?
                    .into()
            }
            FragmentInfo::Literal { start, end } => {
                let literal_fragment_info = PyLiteralFragmentInfo::new(start, end);
                Bound::new(py, literal_fragment_info)?
                    .into_pyobject(py)?
                    .into()
            }
        };

        Ok(Some(frament_info))
    }

    /// Enqueue more bytes to the fragmentizer
    fn enqueue_bytes(&mut self, bytes: Bound<PyBytes>) {
        self.0.enqueue_bytes(bytes.as_bytes())
    }

    /// Retrieve the bytes for the given fragment
    fn fragment_bytes<'a>(
        slf: PyRef<'a, Self>,
        fragment_info: &Bound<PyAny>,
    ) -> PyResult<Bound<'a, PyBytes>> {
        let py = slf.py();
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
        Ok(PyBytes::new(py, bytes))
    }

    /// Return if the current message is completely processed
    fn is_message_complete(&self) -> bool {
        self.0.is_message_complete()
    }

    // Returns whether the current message was explicitly poisoned to prevent decoding
    fn is_message_poisoned(&self) -> bool {
        self.0.is_message_poisoned()
    }

    /// Retrive the bytes of the current message
    fn message_bytes(slf: PyRef<Self>) -> Bound<PyBytes> {
        let py = slf.py();
        let bytes = slf.0.message_bytes();
        PyBytes::new(py, bytes)
    }

    /// Return if the current message exceeded the max message size
    fn is_max_message_size_exceeded(&self) -> bool {
        self.0.is_max_message_size_exceeded()
    }

    /// Skip the current message and start the next message immediately
    fn skip_message(&mut self) {
        self.0.skip_message()
    }

    /// Poisons the current message to prevent its decoding
    fn poison_message(&mut self) {
        self.0.poison_message()
    }

    // TODO izzit good to return string here?
    /// Tries to decode the tag for the current message
    fn decode_tag(slf: PyRef<'_, Self>) -> Option<Bound<'_, PyString>> {
        let py = slf.py();
        let tag = slf.0.decode_tag()?;
        Some(PyString::new(py, tag.inner()))
    }

    /// Tries to decode the current message as greeting
    fn decode_greeting(slf: PyRef<'_, Self>) -> PyResult<PyGreeting> {
        let py = slf.py();
        let codec = GreetingCodec::default();
        match slf.0.decode_message(&codec) {
            Ok(greeting) => Ok(PyGreeting(greeting.to_static())),
            Err(error) => Err(map_decode_message_error(py, error, |_, e| {
                Ok(map_greeting_decode_error(e))
            })?),
        }
    }

    /// Tries to decode the current message as command
    fn decode_command(slf: PyRef<'_, Self>) -> PyResult<PyCommand> {
        let py = slf.py();
        let codec = CommandCodec::default();
        match slf.0.decode_message(&codec) {
            Ok(command) => Ok(PyCommand(command.to_static())),
            Err(error) => Err(map_decode_message_error(py, error, |py, e| {
                map_command_decode_error(py, e)
            })?),
        }
    }

    /// Tries to decode the current message as authenticate data
    fn decode_authenticate_data(slf: PyRef<'_, Self>) -> PyResult<PyAuthenticateData> {
        let py = slf.py();
        let codec = AuthenticateDataCodec::default();
        match slf.0.decode_message(&codec) {
            Ok(authenticate_data) => Ok(PyAuthenticateData(authenticate_data.to_static())),
            Err(error) => Err(map_decode_message_error(py, error, |_, e| {
                Ok(map_authenticate_data_decode_error(e))
            })?),
        }
    }

    /// Tries to decode the current message as response
    fn decode_response(slf: PyRef<'_, Self>) -> PyResult<PyResponse> {
        let py = slf.py();
        let codec = ResponseCodec::default();
        match slf.0.decode_message(&codec) {
            Ok(response) => Ok(PyResponse(response.to_static())),
            Err(error) => Err(map_decode_message_error(py, error, |py, e| {
                map_response_decode_error(py, e)
            })?),
        }
    }

    /// Tries to decode the current message as idle done
    fn decode_idle_done(slf: PyRef<'_, Self>) -> PyResult<PyIdleDone> {
        let py = slf.py();
        let codec = IdleDoneCodec::default();
        match slf.0.decode_message(&codec) {
            Ok(idle_done) => Ok(PyIdleDone(idle_done.to_static())),
            Err(error) => Err(map_decode_message_error(py, error, |_, e| {
                Ok(map_idle_done_decode_error(e))
            })?),
        }
    }
}

fn map_decode_message_error<'a, C>(
    py: Python<'a>,
    decode_message_error: fragmentizer::DecodeMessageError<'a, C>,
    map_failure: impl FnOnce(Python<'a>, C::Error<'a>) -> PyResult<PyErr>,
) -> PyResult<PyErr>
where
    C: Decoder,
    C::Message<'a>: Serialize,
{
    match decode_message_error {
        fragmentizer::DecodeMessageError::DecodingFailure(error) => Err(map_failure(py, error)?),
        fragmentizer::DecodeMessageError::DecodingRemainder { message, remainder } => {
            let dict = pyo3::types::PyDict::new(py);
            dict.set_item("message", serde_pyobject::to_pyobject(py, &message)?)?;
            // TODO izzit good to declassify here?
            // TODO izzit good to use bytes here?
            dict.set_item("remainder", PyBytes::new(py, remainder.declassify()))?;
            Ok(FragmentizerDecodingRemainderError::new_err(dict.unbind()))
        }
        fragmentizer::DecodeMessageError::MessageTooLong { initial } => {
            let dict = pyo3::types::PyDict::new(py);
            // TODO izzit good to declassify here?
            // TODO izzit good to use bytes here?
            dict.set_item("initial", PyBytes::new(py, initial.declassify()))?;
            Ok(FragmentizerMessageTooLongError::new_err(dict.unbind()))
        }
        fragmentizer::DecodeMessageError::MessagePoisoned { discarded } => {
            let dict = pyo3::types::PyDict::new(py);
            // TODO izzit good to declassify here?
            // TODO izzit good to use bytes here?
            dict.set_item("discarded", PyBytes::new(py, discarded.declassify()))?;
            Ok(FragmentizerMessagePoisonedError::new_err(dict.unbind()))
        }
    }
}
