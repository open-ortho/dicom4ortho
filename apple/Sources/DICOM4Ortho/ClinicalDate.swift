// Represents treatment-event dates independently of acquisition instants. Calendar
// arithmetic must not turn daylight-saving transitions into fractional clinical days.
import Foundation

/// A validated Gregorian date with no time of day or timezone.
public struct ClinicalDate: Sendable, Equatable {
    public let year: Int
    public let month: Int
    public let day: Int

    /// Rejects impossible dates rather than normalizing them into another month.
    public init(year: Int, month: Int, day: Int) throws {
        var calendar = Calendar(identifier: .gregorian)
        calendar.timeZone = TimeZone(secondsFromGMT: 0)!
        let components = DateComponents(year: year, month: month, day: day)
        guard (1...9999).contains(year), let date = calendar.date(from: components),
              calendar.component(.year, from: date) == year,
              calendar.component(.month, from: date) == month,
              calendar.component(.day, from: date) == day else {
            throw MaterializationError.invalidClinicalDate
        }
        self.year = year
        self.month = month
        self.day = day
    }

    func days(until other: ClinicalDate) throws -> Int {
        var calendar = Calendar(identifier: .gregorian)
        calendar.timeZone = TimeZone(secondsFromGMT: 0)!
        guard let start = calendar.date(from: DateComponents(year: year, month: month, day: day)),
              let end = calendar.date(from: DateComponents(
                year: other.year, month: other.month, day: other.day)),
              let days = calendar.dateComponents([.day], from: start, to: end).day else {
            throw MaterializationError.invalidClinicalDate
        }
        return days
    }
}
