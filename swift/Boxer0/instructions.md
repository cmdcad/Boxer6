# AverBible - Development Roadmap & Progress

## Project Overview
This is an intelligent reader app built with SwiftUI targeting iOS 15.5+, using MVVM architecture with `ObservableObject`, domain-driven design, and AI-powered text variants & insights.

### SwiftUI Compatibility Rule
The project must compile with Xcode versions older than 16 and an iOS 15.5 deployment target. Prefer APIs available in that SDK, such as `NavigationView`, over newer APIs such as `NavigationStack`. When a newer API is necessary, do not call it directly in a shared view. Isolate it behind an availability-gated, type-erased view modifier and provide an older-platform fallback. This keeps the unavailable selector out of the older compilation path while preserving the enhanced behavior on newer systems.

Example:

```swift
extension View {
	func adaptiveMediumDetent() -> some View {
		modifier(AdaptiveDetentModifier())
	}
}

private struct AdaptiveDetentModifier: ViewModifier {
	func body(content: Content) -> some View {
		if #available(iOS 16.0, *) {
			content.applyNativeDetents()
		} else {
			content.background(SheetDetentConfigurator())
		}
	}
}

extension View {
	@available(iOS 16.0, *)
	fileprivate func applyNativeDetents() -> some View {
		presentationDetents([.medium])
	}
}
```

Use it at the call site instead of calling `.presentationDetents` directly:

```swift
.sheet(isPresented: $isShowingSearch) {
	ReaderSearchView(...)
		.adaptiveMediumDetent()
}
```

Use `@available` wrappers for newer SwiftUI selectors; use `@backDeployed` only when the API specifically supports back deployment. UIKit fallbacks may be used when they are needed to reproduce the behavior on iOS 15.

### Firebase Timestamp Compatibility Rule
Always add Firebase Timestamp support to handle Date fields properly when sending to/decoding from Firebase. Firebase stores dates as Timestamp objects with `{seconds, nanoseconds}` format, not as Date/DateTime primitives. 

Another Rule:
Use `if let c = c { ... }` instead of `if let c { ... }`.

For Swift:
- Implement a `FirebaseTimestamp` struct that matches Firebase's format
- Add custom encoding/decoding logic in `Codable` implementations to handle Timestamp format
- Provide fallback to Date/ISO format for backward compatibility
- Use milliseconds since epoch when needed for numeric compatibility

For C#:
- Implement a `FirebaseTimestamp` class with `Seconds` and `Nanoseconds` properties
- Create a `JsonConverter<DateTime>` that handles Firebase Timestamp format
- Support fallback to milliseconds/ISO date strings for compatibility
- Use `[JsonConverter(typeof(FirebaseTimestampConverter))]` attributes on Date properties

Example Swift Firebase Timestamp:

```swift
struct FirebaseTimestamp: Codable {
    let seconds: Int64
    let nanoseconds: Int64

    init(date: Date) {
        let interval = date.timeIntervalSince1970
        self.seconds = Int64(interval)
        self.nanoseconds = Int64((interval.truncatingRemainder(dividingBy: 1)) * 1_000_000_000)
    }

    var date: Date {
        return Date(timeIntervalSince1970: Double(seconds) + Double(nanoseconds) / 1_000_000_000)
    }
}
```

Example C# Firebase Timestamp Converter:

```csharp
public class FirebaseTimestampConverter : JsonConverter<DateTime>
{
    public override DateTime Read(ref Utf8JsonReader reader, Type typeToConvert, JsonSerializerOptions options)
    {
        if (reader.TokenType == JsonTokenType.StartObject)
        {
            // Handle { "seconds": 1234567890, "nanoseconds": 123456789 }
            reader.Read(); // StartObject
            long seconds = 0;
            long nanoseconds = 0;

            while (reader.Read())
            {
                if (reader.TokenType == JsonTokenType.EndObject)
                    break;

                string? propertyName = reader.GetString();
                reader.Read();

                if (propertyName == "seconds")
                    seconds = reader.GetInt64();
                else if (propertyName == "nanoseconds")
                    nanoseconds = reader.GetInt64();
            }

            return DateTime.UnixEpoch.AddSeconds(seconds).AddTicks(nanoseconds / 100);
        }
        // Fallback to milliseconds or ISO date strings
        else if (reader.TokenType == JsonTokenType.Number)
        {
            double milliseconds = reader.GetDouble();
            return DateTime.UnixEpoch.AddMilliseconds(milliseconds);
        }
        else if (reader.TokenType == JsonTokenType.String)
        {
            string dateString = reader.GetString()!;
            return DateTime.Parse(dateString);
        }

        return DateTime.UtcNow;
    }

    public override void Write(Utf8JsonWriter writer, DateTime value, JsonSerializerOptions options)
    {
        var timestamp = new FirebaseTimestamp(value);
        writer.WriteStartObject();
        writer.WriteNumber("seconds", timestamp.Seconds);
        writer.WriteNumber("nanoseconds", timestamp.Nanoseconds);
        writer.WriteEndObject();
    }
}
```

### Core Principles
- Make the app easy to navigate.
- Make use of the provided assets and be creative. 
- Always ask before doing something big, like changing the overall layout of the app.
- Let the UI be elegant but not overly complex.  
- Let it be beautiful, sleek and user-friendly. 
- Let the user have an enjoyable and seamless reading experience.

---
 
## Technical Specifications
- **Target iOS**: iOS 15.5+
- **Framework**: SwiftUI (MVVM with `@StateObject` / `@Published`)
 