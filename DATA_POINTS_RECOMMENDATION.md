# Garmin Data Points Recommendation

Based on the discovery results from your Garmin fenix 5 Plus, here are my recommendations for the Clawdbot skill.

## High Priority - MUST INCLUDE ✅

These are the core fitness metrics that align with your 2026 goals and provide the most value:

### Daily Activity (from `get_stats`)
- ✅ **totalSteps** - Daily step count
- ✅ **totalDistanceMeters** - Distance traveled (convert to km/miles)
- ✅ **totalKilocalories** - Total calories burned
- ✅ **activeKilocalories** - Active calories (excluding BMR)
- ✅ **bmrKilocalories** - Basal metabolic rate calories
- ✅ **floorsAscended** - Floors climbed
- ✅ **floorsDescended** - Floors descended
- ✅ **moderateIntensityMinutes** - Active time (moderate)
- ✅ **vigorousIntensityMinutes** - Active time (vigorous)
- ✅ **sedentarySeconds** - Inactive time (important for health)

**Why:** Core activity metrics for tracking daily movement and progress toward fitness goals.

### Sleep Quality (from `get_sleep_data`)
- ✅ **sleepTimeSeconds** - Total sleep duration
- ✅ **deepSleepSeconds** - Deep sleep (most restorative)
- ✅ **lightSleepSeconds** - Light sleep
- ✅ **remSleepSeconds** - REM sleep (cognitive recovery)
- ✅ **awakeSleepSeconds** - Time awake during sleep
- ✅ **sleepScores.overall.value** - Overall sleep score (0-100)
- ✅ **sleepScores.qualityScore.value** - Sleep quality
- ✅ **sleepScores.recoveryScore.value** - Recovery score
- ✅ **avgSleepStress** - Average stress during sleep
- ✅ **sleepStartTimestampLocal** - Bedtime
- ✅ **sleepEndTimestampLocal** - Wake time

**Why:** Sleep is critical for fitness recovery and overall health. You want to track improvement here.

### Heart Rate (from `get_heart_rates`)
- ✅ **restingHeartRate** - Daily resting HR (fitness indicator)
- ✅ **minHeartRate** - Lowest HR of the day
- ✅ **maxHeartRate** - Highest HR of the day
- ✅ **lastSevenDaysAvgRestingHeartRate** - Weekly trend

**Why:** Resting heart rate is one of the best indicators of cardiovascular fitness improvement.

### Stress & Recovery (from `get_stress_data`)
- ✅ **averageStressLevel** - Average daily stress (0-100)
- ✅ **maxStressLevel** - Peak stress
- ✅ **restStressDuration** - Time in rest/recovery
- ✅ **lowStressDuration** - Low stress time
- ✅ **mediumStressDuration** - Medium stress time
- ✅ **highStressDuration** - High stress time

**Why:** Stress impacts recovery and performance. Important for work-life balance tracking.

### Body Battery (from `get_body_battery`)
- ✅ **charged** - Energy gained (0-100)
- ✅ **drained** - Energy used
- ✅ **startTimestampGMT** - When measurement started
- ✅ **endTimestampGMT** - When measurement ended
- ✅ **bodyBatteryHighestValue** - Peak energy level
- ✅ **bodyBatteryLowestValue** - Lowest energy level

**Why:** Unique Garmin metric showing energy/readiness. Helps optimize training and recovery.

## Weight & Body Composition - HIGH PRIORITY ⚖️

Critical metrics from your Garmin Index Scale for tracking fitness progress:

### Body Composition (from `get_body_composition`)
- ⚖️ **weight** - Body weight (grams, convert to kg/lbs)
- ⚖️ **bmi** - Body Mass Index
- ⚖️ **bodyFat** - Body fat percentage
- ⚖️ **bodyWater** - Body water percentage
- ⚖️ **muscleMass** - Skeletal muscle mass (grams, convert to kg)
- ⚖️ **boneMass** - Bone mass (grams, convert to kg)
- ⚖️ **visceralFat** - Visceral fat rating (if available)
- ⚖️ **metabolicAge** - Metabolic age (if available)
- ⚖️ **calendarDate** - Date of measurement
- ⚖️ **sourceType** - Data source (INDEX_SCALE)

**Why:** Essential for tracking body composition changes as you improve fitness. Weight alone doesn't tell the story - muscle mass increase + body fat decrease = real progress!

**Current Status (Dec 19, 2025):**
- Weight: 76.93 kg
- Body Fat: 18.4%
- Muscle Mass: 30.86 kg
- BMI: 24.3 (healthy range!)

## Medium Priority - RECOMMENDED 📊

Useful metrics that provide additional insights:

### Respiration (from `get_respiration_data`)
- 📊 **avgWakingRespirationValue** - Average breathing rate while awake
- 📊 **highestRespirationValue** - Peak breathing rate
- 📊 **lowestRespirationValue** - Lowest breathing rate

**Why:** Breathing rate can indicate stress, fitness level, and recovery status.

### Blood Oxygen (from `get_spo2_data`)
- 📊 **latestSpo2** - Most recent SpO2 reading (%)
- 📊 **averageSpo2** - Daily average (if available)
- 📊 **lowestSpo2** - Lowest reading
- 📊 **latestSpo2ReadingTimeLocal** - When measured

**Why:** Useful for altitude training, sleep quality, and overall health monitoring.

### Hydration (from `get_hydration_data`)
- 📊 **valueInML** - Water intake tracking (if manually logged)

**Why:** Important for performance but requires manual logging.

### Performance Metrics (from `get_max_metrics`)
- 📊 **vo2MaxValue** - VO2 Max (aerobic fitness)
- 📊 **vo2MaxPreciseValue** - More accurate VO2 Max
- 📊 **fitnessAge** - Fitness age vs chronological age
- 📊 **altitudeAcclimation** - Altitude adaptation

**Why:** Advanced metrics for serious training. VO2 Max shows aerobic fitness improvement over time.

## Low Priority - OPTIONAL ⚪

Nice to have but lower value:

### Activity Details (from `get_activities`)
- ⚪ Recent workout summaries
- ⚪ Activity type, duration, distance
- ⚪ Average HR during activities

**Why:** Already captured in daily stats. Only needed if you want detailed workout logs.

### Steps Timeline (from `get_steps_data`)
- ⚪ Hourly step breakdown

**Why:** Granular data. Total daily steps are sufficient for most use cases.

## NOT RECOMMENDED ❌

Skip these to keep the skill focused:

- ❌ **Device Settings** - Not available on your device
- ❌ **User Settings** - Not fitness data
- ❌ **Abnormal HR Alerts** - Clinical data, not daily tracking

---

## Recommended CSV Structure

Based on the above, here's my recommended CSV format:

```csv
date,
# Activity
steps,distance_km,calories_total,calories_active,calories_bmr,floors_up,floors_down,
active_minutes_moderate,active_minutes_vigorous,sedentary_hours,
# Sleep
sleep_hours,sleep_deep_min,sleep_light_min,sleep_rem_min,sleep_awake_min,
sleep_score,sleep_quality_score,sleep_recovery_score,
sleep_start,sleep_end,sleep_stress_avg,
# Heart Rate
resting_hr,min_hr,max_hr,avg_hr_7day,
# Stress
stress_avg,stress_max,stress_rest_min,stress_low_min,stress_med_min,stress_high_min,
# Body Battery
bb_charged,bb_drained,bb_high,bb_low,
# Weight & Body Composition
weight_kg,weight_lbs,bmi,body_fat_pct,body_water_pct,
muscle_mass_kg,bone_mass_kg,visceral_fat,metabolic_age,weight_date,
# Health
respiration_avg,respiration_min,respiration_max,
spo2_latest,spo2_avg,spo2_min,
# Performance (optional)
vo2_max,fitness_age,
# Metadata
fetched_at
```

**Total: ~55 columns** - comprehensive tracking of all key health metrics.

## Implementation Priority

### Phase 1 (MVP) - Launch with these:
1. Daily Activity (steps, distance, calories, floors)
2. Sleep (duration, stages, score)
3. Heart Rate (resting, min, max)
4. Stress (average, time in each zone)
5. Body Battery (charged, drained, high, low)
6. Weight & Body Composition (weight, BMI, body fat, muscle mass)

**Estimated: ~35 core columns**

### Phase 2 (Enhanced) - Add later:
1. Respiration data
2. SpO2 data
3. VO2 Max & fitness metrics
4. Hydration (if manually logged)

**Additional: ~10 columns**

### Phase 3 (Advanced) - Future:
1. Activity-level details (individual workouts)
2. Hourly breakdowns (steps, HR)
3. Training load & recovery metrics

## Alignment with Your 2026 Goals

### Goal: Improve Fitness
**Key Metrics:**
- Steps (target: 10,000/day)
- Active minutes
- Resting HR (should decrease as fitness improves)
- VO2 Max (should increase)
- Body Battery (better recovery = higher charged values)
- **Weight & Body Composition:**
  - Body fat % (decrease)
  - Muscle mass (increase or maintain)
  - Weight (track overall trend)
  - BMI (healthy range: 18.5-24.9)

### Goal: Improve Golf Game
**Key Metrics:**
- Sleep quality (impacts coordination)
- Stress levels (lower stress = better performance)
- Body Battery (need high energy for 18 holes)

### Goal: President Role (Reduce Stress)
**Key Metrics:**
- Stress averages and trends
- Sleep quality and duration
- Body Battery recovery

---

## My Recommendation

**Start with Phase 1 (MVP)** - 35 core columns covering:
- Activity
- Sleep
- Heart Rate  
- Stress
- Body Battery
- **Weight & Body Composition** ⚖️

This gives you:
✅ All data needed for your 2026 goals  
✅ Comprehensive daily health snapshot  
✅ **Complete body composition tracking** (weight, fat, muscle)
✅ Trend analysis capabilities  
✅ Not overwhelming with too many metrics  

**Add Phase 2** after a few weeks of successful tracking.

Want me to update `fetch_garmin.py` to collect these recommended data points?
