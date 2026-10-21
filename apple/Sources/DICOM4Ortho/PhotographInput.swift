// Separates source evidence from output compression policy. No case opens a camera,
// fetches a URL, or claims codec support merely because a syntax UID is known.
import Foundation

/// One still photograph supplied by the application.
public enum PhotographInput: Sendable {
    /// Row-major interleaved RGB, eight bits per component, no alpha or row padding.
    case rgb8(Data, width: Int, height: Int)
    /// Encoded image bytes. The implementation checks content, not a filename suffix.
    case encoded(Data)
    /// A local encoded-image file. Non-file URLs are rejected; the file is read once.
    case file(URL)
}
