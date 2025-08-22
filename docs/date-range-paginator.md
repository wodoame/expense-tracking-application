# DateRangePaginator Class Documentation

## Overview
The `DateRangePaginator` is a utility class located in `core/datechecker.py` that provides date-based pagination functionality. Unlike traditional pagination that works with item counts, this class divides a date range into manageable chunks for display or processing.

## Purpose
This class is designed to:
- Break down large date ranges into smaller, paginated chunks
- Support both forward (oldest first) and reverse (newest first) pagination
- Handle edge cases where the total date range isn't evenly divisible by the page size
- Provide a consistent interface for date-based pagination across the application

## Class Definition

```python
class DateRangePaginator:
    def __init__(self, start_date, end_date, dates_per_page, reverse=False)
    def get_date_range(self, page_number) -> Tuple[datetime, datetime]
    def get_total_pages(self) -> int
```

## Constructor Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `start_date` | `Union[datetime, str]` | The starting date of the range (datetime object or 'YYYY-MM-DD' string) | Required |
| `end_date` | `Union[datetime, str]` | The ending date of the range (datetime object or 'YYYY-MM-DD' string) | Required |
| `dates_per_page` | `int` | Number of days to include in each page | Required |
| `reverse` | `bool` | If True, pagination starts from end_date and moves backward | `False` |

## Methods

### `get_date_range(page_number: int) -> Tuple[datetime, datetime]`

Returns the date range for a specific page number.

**Parameters:**
- `page_number` (int): The page number (1-indexed)

**Returns:**
- Tuple containing (start_date, end_date) for the page
- In reverse mode: Returns (end_date, start_date) for the page

**Raises:**
- `ValueError`: If the page number is invalid (not between 1 and total_pages)

### `get_total_pages() -> int`

Returns the total number of pages required to paginate the entire date range.

**Returns:**
- `int`: Total number of pages

## Pagination Modes

### Normal Mode (reverse=False)
Pages are created from start_date to end_date:
- Page 1: `start_date` to `start_date + dates_per_page - 1`
- Page 2: `start_date + dates_per_page` to `start_date + 2×dates_per_page - 1`
- And so on...

### Reverse Mode (reverse=True)
Pages are created from end_date to start_date:
- Page 1: `end_date` to `end_date - dates_per_page + 1`
- Page 2: `end_date - dates_per_page` to `end_date - 2×dates_per_page + 1`
- And so on...

## Edge Case Handling

### Uneven Division
When the total date range isn't evenly divisible by `dates_per_page`, the last page will contain fewer days:

- **Total pages calculation**: Uses ceiling division `(total_days + dates_per_page - 1) // dates_per_page`
- **Boundary protection**: Uses `min()` and `max()` functions to ensure pages don't exceed the original date range

### Example
Date range: January 1-10, 2025 (10 days), with 7 days per page:
- **Total pages**: 2
- **Page 1**: Jan 1-7 (7 days)
- **Page 2**: Jan 8-10 (3 days only)

## Usage Examples

### Basic Usage
```python
from core.datechecker import DateRangePaginator
from datetime import datetime

# Create paginator for a month with weekly pages
paginator = DateRangePaginator(
    start_date="2025-01-01",
    end_date="2025-01-31",
    dates_per_page=7
)

# Get first week
first_week = paginator.get_date_range(1)
# Returns: (datetime(2025, 1, 1), datetime(2025, 1, 7))

# Get total number of weeks
total_weeks = paginator.get_total_pages()  # Returns: 5
```

### Reverse Pagination (Newest First)
```python
# Show most recent expenses first
paginator = DateRangePaginator(
    start_date=user.date_joined.date(),
    end_date=datetime.now().date(),
    dates_per_page=7,
    reverse=True  # Start from most recent
)

# Get most recent week
recent_week = paginator.get_date_range(1)
# Returns most recent 7 days
```

### Processing All Pages
```python
paginator = DateRangePaginator("2025-01-01", "2025-12-31", 30)

for page_num in range(1, paginator.get_total_pages() + 1):
    start_date, end_date = paginator.get_date_range(page_num)
    print(f"Page {page_num}: {start_date} to {end_date}")
    # Process expenses for this date range
```

## Use Cases in Expense Tracking Application

1. **Expense Timeline Pagination**: Break down a user's entire expense history into manageable date chunks
2. **Recent Activity Display**: Show recent expenses first using reverse pagination
3. **Weekly/Monthly Reports**: Generate reports for specific time periods
4. **Performance Optimization**: Avoid loading all expenses at once by paginating by date ranges
5. **Calendar Integration**: Display expenses organized by time periods

## Integration with Other Components

The `DateRangePaginator` is typically used alongside:
- **EnhancedExpensePaginator**: For combining date-based and count-based pagination
- **Product Models**: To filter expenses within specific date ranges
- **Frontend Components**: To display paginated expense data in the UI

## Error Handling

The class includes validation for:
- **Invalid date ranges**: `end_date` must be ≥ `start_date`
- **Invalid page size**: `dates_per_page` must be positive
- **Invalid page numbers**: Must be between 1 and `total_pages`

## Performance Considerations

- **Memory efficient**: Only calculates date ranges on demand
- **O(1) complexity**: Date range calculation is constant time
- **No database queries**: Pure date arithmetic operations
- **Lightweight**: Minimal memory footprint

## Related Documentation

- [Project Structure](project-structure.md)
- [General Structure of a Page](general-structure-of-a-page.md)
- [Page Implementations](page-implementations.md)

---

**Note**: This class is part of the core date handling utilities and is essential for the application's pagination system. Any modifications should maintain backward compatibility with existing pagination implementations.
