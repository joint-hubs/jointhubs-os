---
name: travel-research
description: |
  Strategies for finding best accommodation, flights, and travel deals.
  Use when: "find hotel", "book accommodation", "compare flights", "travel deals", "best price".
---

# Travel Research

Find the best travel deals through systematic research and comparison.

## When to Use

- Searching for accommodation (hotels, Airbnb, hostels)
- Comparing flight options
- Finding deals and discounts
- Evaluating neighborhoods to stay
- Checking reviews and red flags

---

## Accommodation Research

### Platform Hierarchy

Check these platforms in order — prices vary significantly:

| Platform | Best For | Quirks |
|----------|----------|--------|
| **Booking.com** | Hotels, last-minute | Genius discounts, free cancellation common |
| **Airbnb** | Apartments, long stays | Weekly/monthly discounts, cleaning fees add up |
| **Hotels.com** | Loyalty (10th night free) | Good for frequent travelers |
| **Hostelworld** | Budget, social | Book direct after finding for better rates |
| **Google Hotels** | Meta-search comparison | Shows all platforms, tracks price drops |
| **Direct booking** | Best price guarantee | Often 5-10% cheaper than OTAs |

### The Comparison Workflow

```
1. Start with Google Hotels → get price range baseline
2. Check Booking.com → note Genius price if applicable
3. Check Airbnb → calculate TOTAL (base + cleaning + service fee)
4. Find the property's direct website → often cheapest
5. Check cancellation policies before deciding
```

### Airbnb Total Cost Calculator

Airbnb prices are deceptive. Always calculate the **true nightly rate**:

```
True nightly rate = (Base price × nights + Cleaning fee + Service fee) ÷ nights

Example:
- Listed: €80/night for 3 nights
- Cleaning: €45
- Service fee: €35
- True cost: (240 + 45 + 35) ÷ 3 = €107/night (34% higher!)
```

**Pro tip**: Longer stays dilute fixed fees. A 7-night stay with €45 cleaning = €6.50/night overhead.

### Hidden Costs Checklist

Always check for:

- [ ] **City/tourist tax** — €1-5/person/night (not always in upfront price)
- [ ] **Resort fees** — Common in US, Vegas especially
- [ ] **Parking** — Hotels charge €15-40/night in cities
- [ ] **Breakfast** — Often €15-25/person, nearby café may be cheaper
- [ ] **WiFi** — Still charged at some business hotels
- [ ] **Airport distance** — Cheap hotel + €50 taxi = not cheap

### Review Analysis

Don't just check the score. Read strategically:

```
1. Sort by "Most recent" — things change
2. Read 2-3 star reviews first — real issues, not nitpicks
3. Look for patterns — one complaint is noise, three is signal
4. Check photos from guests, not just the listing
5. Note review count — 4.2 with 500 reviews beats 4.8 with 12
```

**Red flags:**
- "Construction" or "renovation" mentioned recently
- Multiple mentions of noise/cleanliness
- Host responses that are defensive, not helpful
- "Not as pictured" in multiple reviews

### Neighborhood Selection

Before picking a property, understand the area:

```
1. Google Maps → zoom to neighborhood
2. Check walking distance to your priorities
3. Look for metro/transit stops
4. Search "[City] where to stay reddit" for local advice
5. Avoid: too far from center, dead at night, tourist traps
```

**The 15-minute test**: Can you walk to 3 things you'll use daily in 15 min? (Coffee, metro, grocery)

### Booking Strategy by Trip Type

| Trip Type | Strategy |
|-----------|----------|
| **Weekend city break** | Book refundable now, keep watching for better deals |
| **Peak season** | Book 2-3 months ahead, prices only go up |
| **Shoulder season** | Wait for last-minute deals (1-2 weeks out) |
| **Long stay (7+ days)** | Negotiate direct, ask for weekly rate |
| **Work trip** | Prioritize WiFi/desk reviews, check expense policy |

---

## Flight Research

### Search Strategy

```
1. Google Flights → explore flexible dates, see price calendar
2. Skyscanner "Everywhere" → if destination flexible
3. Check budget airlines direct (Ryanair, Wizz often excluded from aggregators)
4. Set price alerts → book when it drops
```

### Timing Guidelines

| Route Type | Book Ahead | Best Days to Fly |
|------------|------------|------------------|
| Domestic/Short-haul | 1-3 weeks | Tue, Wed, Sat |
| Europe | 2-6 weeks | Midweek |
| Long-haul | 2-3 months | Varies |
| Peak holiday | 3-4 months | Any (just book early) |

### Budget Airline Reality Check

The €19 flight is never €19:

```
Base fare: €19
+ Seat selection: €8
+ Cabin bag: €25
+ Checked bag: €35
+ Priority boarding: €6
+ Travel insurance: €12
= Real cost: €105

Compare to legacy carrier at €89 with bags included
```

### Layover Trade-offs

| Layover | Price Saved | Worth It? |
|---------|-------------|-----------|
| < 2 hours | Any | ⚠️ Risky for connections |
| 2-4 hours | €50+ | ✅ Usually fine |
| 5-8 hours | €100+ | 🤔 Depends on airport |
| Overnight | €150+ | ❌ Unless you enjoy suffering |

---

## Deal-Finding Tactics

### Price Drop Monitoring

Set up alerts:
- **Google Flights** — Built-in tracking
- **Hopper** — ML-predicted best time to book
- **Skyscanner** — Price alerts for routes

### Loyalty Math

Is the points/miles game worth it?

```
Quick rule: 1 point ≈ €0.01 (varies widely)

Example:
- Hotel: €150/night or 15,000 points
- Point value: €150 ÷ 15,000 = €0.01/point ✓ Fair deal
- If you earned points from credit card spend, may be worth it
- If buying points: usually terrible value
```

### Last-Minute Strategies

For spontaneous trips:
- **HotelTonight** — Same-day hotel deals
- **Airbnb last-minute** — Filter by "Instant Book"
- **Hostelworld** — Often has availability when hotels don't
- **Call hotels directly** — Empty rooms get discounted

---

## Output Templates

### Accommodation Comparison Table

```markdown
| Property | Platform | Per Night | Total | Cancel Policy | Distance | Rating |
|----------|----------|-----------|-------|---------------|----------|--------|
| Hotel A  | Booking  | €95       | €285  | Free until 24h| 800m     | 8.4    |
| Apt B    | Airbnb   | €75+€40   | €265  | Moderate      | 1.2km    | 4.7    |
| Hotel A  | Direct   | €89       | €267  | Flexible      | 800m     | -      |

**Recommendation**: Book Hotel A direct — best price + flexibility
```

### Flight Options Summary

```markdown
## ✈️ [Origin] → [Destination] | [Dates]

**Option 1 — Best Value** 
Ryanair | 07:15→09:30 | €67 (with cabin bag)
⚠️ Early morning, no checked bag

**Option 2 — Balanced**
Lufthansa | 14:20→16:40 | €112 (23kg included)  
✅ Good timing, bags included

**Option 3 — Premium**
Direct LOT | 11:00→13:15 | €145
✅ Best schedule, full service

**My take**: Option 2 unless you're packing light
```

---

## Common Mistakes to Avoid

1. **Booking the cheapest without reading reviews** — €30 saved, terrible sleep
2. **Ignoring total cost on Airbnb** — Cleaning fees lie in wait
3. **Not checking direct booking** — OTAs take 15-20% commission, hotels match or beat
4. **Assuming airport hotels are convenient** — Often far from everything + boring
5. **Skipping cancellation policy** — Life happens, flexibility has value
6. **Booking non-refundable too early** — Plans change, pay the €10 extra

---

*The best deal isn't the cheapest — it's the one you don't regret.*
