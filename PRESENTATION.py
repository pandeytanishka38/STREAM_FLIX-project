
# ============================================================
# STREAM FLIX OTT ANALYTICS DASHBOARD
# PHASE 1: DATA CLEANING & VALIDATION
# PHASE 2: PROFESSIONAL DASHBOARD (10 CHARTS)
# PHASE 3: BUSINESS KPIs (10 KPI CARDS)
# ============================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import MaxNLocator
from pathlib import Path

# ============================================================
# CONFIGURATION
# ============================================================

DATA_PATH = Path("C:/Users/asus/Desktop/project44")

FILES = {
    "subscribers": "subscribers.csv",
    "reviews": "reviews.csv",
    "watch_history": "watch_history.csv",
    "titles": "titles.csv",
    "ratings": "ratings.csv",
    "watchlist": "watchlist.csv"
}

# Professional dashboard colors
NAVY = "#142D4E"
BLUE = "#2878B5"
LIGHT_BLUE = "#DCEEFF"
GREEN = "#239B56"
RED = "#E74C3C"
ORANGE = "#F39C12"
PURPLE = "#8254A8"
TEAL = "#168F91"
GREY = "#788493"
BACKGROUND = "#F1F5FA"
WHITE = "#FFFFFF"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 9,
    "axes.titlesize": 11,
    "axes.titleweight": "bold",
    "axes.labelsize": 9,
    "figure.facecolor": BACKGROUND,
    "axes.facecolor": WHITE
})


# ============================================================
# PHASE 1: DATA CLEANING & VALIDATION
# ============================================================

print("\n" + "=" * 55)
print("PHASE 1: DATA CLEANING & VALIDATION")
print("=" * 55)

# ---------------- LOAD DATASETS ----------------

print("\nLOADING DATASETS")

datasets = {}

for name, filename in FILES.items():

    file_path = DATA_PATH / filename

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    df = pd.read_csv(file_path)

    # Standardize column names
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_", regex=False)
    )

    datasets[name] = df

subscribers = datasets["subscribers"]
reviews = datasets["reviews"]
watch_history = datasets["watch_history"]
titles = datasets["titles"]
ratings = datasets["ratings"]
watchlist = datasets["watchlist"]

print("All six datasets loaded successfully!")

# ---------------- DISPLAY FIRST 5 ROWS ----------------

for name, df in datasets.items():

    print(f"\n{name.upper()} - FIRST 5 ROWS")
    print(df.head())

# ---------------- DATASET INFORMATION ----------------

print("\n" + "=" * 55)
print("ROWS, COLUMNS & DATA TYPES")
print("=" * 55)

for name, df in datasets.items():

    print(f"\n{name.upper()}")
    print("Rows:", df.shape[0])
    print("Columns:", df.shape[1])
    print(df.dtypes)

# ---------------- MISSING VALUES ----------------

print("\n" + "=" * 55)
print("MISSING VALUES")
print("=" * 55)

for name, df in datasets.items():

    print(f"\n{name.upper()}")
    print(df.isnull().sum())


# ---------------- DATE CONVERSION ----------------

print("\nDATE CONVERSION")

subscribers["signup_date"] = pd.to_datetime(
    subscribers["signup_date"],
    errors="coerce"
)

watch_history["watch_date"] = pd.to_datetime(
    watch_history["watch_date"],
    errors="coerce"
)

# ---------------- NUMERIC CONVERSION ----------------

numeric_columns = {
    "watch_history": [
        "watch_duration_min",
        "completion_pct"
    ],
    "subscribers": [
        "monthly_price_usd"
    ],
    "ratings": [
        "rating"
    ],
    "titles": [
        "release_year",
        "total_plays"
    ]
}

for dataset_name, columns in numeric_columns.items():

    df = datasets[dataset_name]

    for col in columns:

        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col],
                errors="coerce"
            )

# Convert fractional completion values to percentage.
if "completion_pct" in watch_history.columns:

    if (
        watch_history["completion_pct"].dropna().size > 0
        and watch_history["completion_pct"].max() <= 1
    ):
        watch_history["completion_pct"] *= 100

# Convert boolean columns safely.
def convert_boolean(series):

    mapping = {
        "true": True,
        "false": False,
        "1": True,
        "0": False,
        "yes": True,
        "no": False
    }

    return (
        series.astype(str)
        .str.strip()
        .str.lower()
        .map(mapping)
        .fillna(False)
        .astype(bool)
    )


for df, column in [
    (subscribers, "is_active"),
    (watchlist, "watched"),
    (titles, "is_original")
]:

    if column in df.columns:
        df[column] = convert_boolean(df[column])

print("Date and numeric conversions completed.")

# ---------------- NEGATIVE VALUE CHECK ----------------

print("\n" + "=" * 55)
print("NEGATIVE VALUE CHECK")
print("=" * 55)

negative_duration = (
    watch_history["watch_duration_min"] < 0
).sum()

negative_price = (
    subscribers["monthly_price_usd"] < 0
).sum()

print("Negative Watch Duration:", negative_duration)
print("Negative Monthly Price:", negative_price)

# Invalid negative values are excluded from calculations.
watch_history.loc[
    watch_history["watch_duration_min"] < 0,
    "watch_duration_min"
] = np.nan

subscribers.loc[
    subscribers["monthly_price_usd"] < 0,
    "monthly_price_usd"
] = np.nan

# ---------------- OUTLIER DETECTION ----------------

print("\n" + "=" * 55)
print("OUTLIER DETECTION")
print("=" * 55)

Q1 = watch_history["watch_duration_min"].quantile(0.25)
Q3 = watch_history["watch_duration_min"].quantile(0.75)

IQR = Q3 - Q1

lower = Q1 - 1.5 * IQR
upper = Q3 + 1.5 * IQR

outliers = watch_history[
    (watch_history["watch_duration_min"] < lower) |
    (watch_history["watch_duration_min"] > upper)
]

print("Outliers Found:", len(outliers))

# Outliers are reported, not automatically deleted.

# ---------------- REFERENTIAL INTEGRITY ----------------

print("\n" + "=" * 55)
print("REFERENTIAL INTEGRITY")
print("=" * 55)

invalid_subscriber = watch_history[
    ~watch_history["subscriber_id"].isin(
        subscribers["subscriber_id"]
    )
]

invalid_title = watch_history[
    ~watch_history["title_id"].isin(
        titles["title_id"]
    )
]

print("Invalid Subscriber IDs:", len(invalid_subscriber))
print("Invalid Title IDs:", len(invalid_title))

# ---------------- DATA QUALITY SUMMARY ----------------

print("\n" + "=" * 55)
print("DATA QUALITY SUMMARY")
print("=" * 55)

for name, df in datasets.items():

    print(f"{name.upper()}: {df.shape}")

print("\nPHASE 1 COMPLETED SUCCESSFULLY!")


# ============================================================
# PHASE 2: DASHBOARD
# ============================================================

print("\n" + "=" * 55)
print("PHASE 2: STREAM FLIX DASHBOARD")
print("=" * 55)

# ---------------- HELPER FUNCTIONS ----------------

def empty_chart(ax, message="No data available"):

    ax.text(
        0.5, 0.5,
        message,
        ha="center",
        va="center",
        transform=ax.transAxes,
        color=GREY
    )

    ax.set_xticks([])
    ax.set_yticks([])


def style_axis(ax):

    ax.set_facecolor(WHITE)

    ax.grid(
        axis="y",
        linestyle="--",
        alpha=0.25,
        color=GREY
    )

    ax.set_axisbelow(True)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.tick_params(
        axis="both",
        labelsize=8,
        pad=4
    )


# ---------------- MONTHLY DATA ----------------

monthly_viewing = (
    watch_history
    .dropna(subset=["watch_date"])
    .set_index("watch_date")
    ["watch_duration_min"]
    .resample("MS")
    .sum() / 60
)

monthly_activity = (
    watch_history
    .dropna(subset=["watch_date"])
    .set_index("watch_date")
    .resample("MS")
    .size()
)

# ---------------- DASHBOARD LAYOUT ----------------

fig = plt.figure(figsize=(25, 17))

fig.patch.set_facecolor(BACKGROUND)

fig.suptitle(
    "STREAM FLIX | OTT ANALYTICS DASHBOARD",
    fontsize=25,
    fontweight="bold",
    color=NAVY,
    y=0.985
)

gs = fig.add_gridspec(
    4, 5,
    left=0.045,
    right=0.985,
    top=0.925,
    bottom=0.065,
    wspace=0.38,
    hspace=0.55,
    height_ratios=[0.65, 0.65, 2.2, 2.2]
)

# First two rows are KPI cards.
# Last two rows contain 10 charts.

axes = []

for row in range(2, 4):

    for col in range(5):

        ax = fig.add_subplot(gs[row, col])

        style_axis(ax)

        axes.append(ax)


# ============================================================
# CHART 1: MONTHLY VIEWING VOLUME
# ============================================================

ax = axes[0]

if len(monthly_viewing):

    ax.plot(
        monthly_viewing.index,
        monthly_viewing.values,
        color=BLUE,
        linewidth=2.5
    )

    ax.fill_between(
        monthly_viewing.index,
        monthly_viewing.values,
        color=LIGHT_BLUE,
        alpha=0.7
    )

    locator = mdates.AutoDateLocator(minticks=3, maxticks=6)

    ax.xaxis.set_major_locator(locator)

    ax.xaxis.set_major_formatter(
        mdates.ConciseDateFormatter(locator)
    )

    ax.set_ylabel("Watch Hours")
    ax.set_xlabel("Month")

else:

    empty_chart(ax)

ax.set_title("Monthly Viewing Volume", pad=12)


# ============================================================
# CHART 2: MONTHLY WATCH ACTIVITY
# ============================================================

ax = axes[1]

if len(monthly_activity):

    ax.plot(
        monthly_activity.index,
        monthly_activity.values,
        color=RED,
        linewidth=2.5,
        marker="o",
        markersize=3
    )

    locator = mdates.AutoDateLocator(minticks=3, maxticks=6)

    ax.xaxis.set_major_locator(locator)

    ax.xaxis.set_major_formatter(
        mdates.ConciseDateFormatter(locator)
    )

    ax.set_ylabel("Watch Sessions")
    ax.set_xlabel("Month")

else:

    empty_chart(ax)

ax.set_title("Monthly Watch Activity", pad=12)


# ============================================================
# CHART 3: MOVIES VS TV SHOWS
# ============================================================

ax = axes[2]

type_counts = titles["type"].dropna().value_counts()

if len(type_counts):

    ax.pie(
        type_counts.values,
        labels=type_counts.index,
        autopct="%1.1f%%",
        startangle=90,
        colors=[BLUE, RED, GREEN, ORANGE],
        textprops={"fontsize": 9},
        wedgeprops={
            "edgecolor": WHITE,
            "linewidth": 1.5
        }
    )

    ax.axis("equal")

else:

    empty_chart(ax)

ax.set_title("Movies vs TV Shows", pad=12)


# ============================================================
# CHART 4: TOP 10 GENRES
# ============================================================

ax = axes[3]

genre_counts = (
    titles["primary_genre"]
    .dropna()
    .value_counts()
    .head(10)
    .sort_values()
)

if len(genre_counts):

    ax.barh(
        genre_counts.index,
        genre_counts.values,
        color=GREEN
    )

    ax.set_xlabel("Number of Titles")

else:

    empty_chart(ax)

ax.set_title("Top 10 Genres", pad=12)


# ============================================================
# CHART 5: TOP 10 COUNTRIES
# ============================================================

ax = axes[4]

country_counts = (
    titles["country"]
    .dropna()
    .value_counts()
    .head(10)
    .sort_values()
)

if len(country_counts):

    ax.barh(
        country_counts.index,
        country_counts.values,
        color=ORANGE
    )

    ax.set_xlabel("Number of Titles")

else:

    empty_chart(ax)

ax.set_title("Top 10 Countries", pad=12)


# ============================================================
# CHART 6: DEVICE USAGE
# ============================================================

ax = axes[5]

device_counts = (
    watch_history["device"]
    .dropna()
    .value_counts()
    .head(10)
    .sort_values()
)

if len(device_counts):

    ax.barh(
        device_counts.index,
        device_counts.values,
        color=PURPLE
    )

    ax.set_xlabel("Watch Sessions")

else:

    empty_chart(ax)

ax.set_title("Device Usage", pad=12)


# ============================================================
# CHART 7: RATINGS DISTRIBUTION
# ============================================================

ax = axes[6]

rating_counts = (
    ratings["rating"]
    .dropna()
    .value_counts()
    .sort_index()
)

if len(rating_counts):

    ax.bar(
        rating_counts.index.astype(str),
        rating_counts.values,
        color="#79C5E8",
        edgecolor=NAVY,
        linewidth=0.5
    )

    ax.set_xlabel("Rating")
    ax.set_ylabel("Number of Ratings")

else:

    empty_chart(ax)

ax.set_title("Ratings Distribution", pad=12)


# ============================================================
# CHART 8: REVIEW SENTIMENT
# ============================================================

ax = axes[7]

sentiment_counts = (
    reviews["sentiment"]
    .dropna()
    .astype(str)
    .str.title()
    .value_counts()
)

if len(sentiment_counts):

    color_map = {
        "Positive": GREEN,
        "Neutral": GREY,
        "Negative": RED
    }

    colors = [
        color_map.get(value, BLUE)
        for value in sentiment_counts.index
    ]

    ax.bar(
        sentiment_counts.index,
        sentiment_counts.values,
        color=colors
    )

    ax.set_ylabel("Number of Reviews")

else:

    empty_chart(ax)

ax.set_title("Review Sentiment", pad=12)


# ============================================================
# CHART 9: RECENT RELEASE YEARS
# ============================================================

ax = axes[8]

year_counts = (
    titles["release_year"]
    .dropna()
    .astype(int)
    .value_counts()
    .sort_index()
    .tail(12)
)

if len(year_counts):

    ax.plot(
        year_counts.index,
        year_counts.values,
        color=RED,
        marker="o",
        linewidth=2.5,
        markersize=5
    )

    ax.set_xlabel("Release Year")
    ax.set_ylabel("Number of Titles")

    ax.xaxis.set_major_locator(
        MaxNLocator(integer=True, nbins=6)
    )

else:

    empty_chart(ax)

ax.set_title("Recent Release Years", pad=12)


# ============================================================
# CHART 10: TOP WATCHLIST
# ============================================================

ax = axes[9]

watchlist_column = (
    "title_id" if "title_id" in watchlist.columns
    else watchlist.columns[0]
)

watchlist_counts = (
    watchlist[watchlist_column]
    .dropna()
    .value_counts()
    .head(10)
    .sort_values()
)

if len(watchlist_counts):

    ax.barh(
        watchlist_counts.index.astype(str),
        watchlist_counts.values,
        color=TEAL
    )

    ax.set_xlabel("Watchlist Entries")

else:

    empty_chart(ax)

ax.set_title("Top 10 Watchlist", pad=12)


# ---------------- FINAL CHART FORMATTING ----------------

for ax in axes:

    ax.tick_params(
        axis="both",
        labelsize=7
    )

    ax.margins(x=0.08, y=0.08)

# ============================================================
# PHASE 3: BUSINESS KPIs
# ============================================================

print("\n" + "=" * 55)
print("PHASE 3: BUSINESS KPI ANALYSIS")
print("=" * 55)

# ---------------- TOTAL WATCH HOURS ----------------

total_watch_hours = (
    watch_history["watch_duration_min"]
    .sum() / 60
)

# ---------------- ACTIVE RATE ----------------

total_subscribers = len(subscribers)

active_subscribers = (
    subscribers["is_active"].sum()
    if total_subscribers else 0
)

active_rate = (
    active_subscribers / total_subscribers * 100
    if total_subscribers else 0
)

# ---------------- CHURN RATE ----------------

inactive_subscribers = (
    total_subscribers - active_subscribers
)

churn_rate = (
    inactive_subscribers / total_subscribers * 100
    if total_subscribers else 0
)

# ---------------- COMPLETION RATE ----------------

avg_completion = (
    watch_history["completion_pct"].mean()
)

avg_completion = (
    avg_completion if pd.notna(avg_completion) else 0
)

# ---------------- MONTHLY REVENUE ----------------

active_users = subscribers[
    subscribers["is_active"] == True
]

mrr = active_users[
    "monthly_price_usd"
].sum()

# ---------------- ARPU ----------------

arpu = (
    mrr / active_subscribers
    if active_subscribers else 0
)

# ---------------- AVG WATCH TIME ----------------

avg_watch_time = (
    watch_history
    .groupby("subscriber_id")["watch_duration_min"]
    .sum()
    .mean() / 60
)

avg_watch_time = (
    avg_watch_time
    if pd.notna(avg_watch_time) else 0
)

# ---------------- WATCHLIST CONVERSION ----------------

conversion = (
    watchlist["watched"].mean() * 100
    if len(watchlist) else 0
)

# ---------------- HIT CONCENTRATION ----------------

top10_titles = max(
    1,
    int(np.ceil(len(titles) * 0.10))
) if len(titles) else 0

top_plays = (
    titles.nlargest(
        top10_titles,
        "total_plays"
    )["total_plays"].sum()
    if top10_titles else 0
)

total_plays = titles["total_plays"].sum()

hit_concentration = (
    top_plays / total_plays * 100
    if total_plays > 0 else 0
)

# ---------------- ORIGINAL SHARE OF HOURS ----------------

merged = watch_history.merge(
    titles[["title_id", "is_original"]].drop_duplicates("title_id"),
    on="title_id",
    how="left"
)

total_hours = (
    merged["watch_duration_min"].sum() / 60
)

original_hours = (
    merged.loc[
        merged["is_original"] == True,
        "watch_duration_min"
    ].sum() / 60
)

original_share = (
    original_hours / total_hours * 100
    if total_hours > 0 else 0
)

# ============================================================
# KPI SUMMARY
# ============================================================

kpis = [

    ("TOTAL WATCH HOURS",
     f"{total_watch_hours:,.0f} Hrs",
     BLUE),

    ("ACTIVE RATE",
     f"{active_rate:.1f}%",
     GREEN),

    ("CHURN RATE",
     f"{churn_rate:.1f}%",
     RED),

    ("COMPLETION RATE",
     f"{avg_completion:.1f}%",
     PURPLE),

    ("MONTHLY REVENUE",
     f"${mrr:,.0f}",
     ORANGE),

    ("ARPU",
     f"${arpu:.2f}",
     TEAL),

    ("AVG WATCH TIME",
     f"{avg_watch_time:.1f} Hrs",
     BLUE),

    ("WATCHLIST CONVERSION",
     f"{conversion:.1f}%",
     GREEN),

    ("HIT CONCENTRATION",
     f"{hit_concentration:.1f}%",
     PURPLE),

    ("ORIGINAL SHARE",
     f"{original_share:.1f}%",
     ORANGE)
]

# ---------------- KPI CARDS ----------------

for i, (label, value, color) in enumerate(kpis):

    row = i // 5
    col = i % 5

    ax = fig.add_subplot(gs[row, col])

    ax.set_facecolor(GREY)

    ax.set_xticks([])
    ax.set_yticks([])

    for spine in ax.spines.values():
        spine.set_visible(False)

    # KPI heading
    ax.text(
        0.5, 0.78,
        label,
        transform=ax.transAxes,
        ha="center",
        fontsize=9,
        fontweight="bold",
        color=WHITE
    )

    # KPI value
    ax.text(
        0.5, 0.38,
        value,
        transform=ax.transAxes,
        ha="center",
        fontsize=19,
        fontweight="bold",
        color=RED
    )

# ---------------- SAVE DASHBOARD ----------------

plt.savefig(
    DATA_PATH / "STREAM_FLIX_DASHBOARD.png",
    dpi=250,
    bbox_inches="tight",
    facecolor=BACKGROUND
)

plt.show()

# ============================================================
# PRINT KPI SUMMARY
# ============================================================

print("\n" + "=" * 55)
print("STREAM FLIX KPI SUMMARY")
print("=" * 55)

for label, value, color in kpis:

    print(f"{label:<25}: {value}")

print("\n" + "=" * 55)
print("ALL THREE PHASES COMPLETED SUCCESSFULLY!")
print("=" * 55)

print("\nDashboard saved successfully:")
print(DATA_PATH / "STREAM_FLIX_DASHBOARD.png")
