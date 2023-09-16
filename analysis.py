import re

import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from wordcloud import WordCloud


def load_data():
    """
    Load CSV files into pandas dataframes.
    """
    faculty_table = pd.read_csv('faculty_table.csv')
    faculty_grad_year = pd.read_csv('faculty_grad_year.csv')
    return faculty_table, faculty_grad_year


def basic_eda(df):
    """
    Display basic statistics and information of the given dataframe.
    """
    print(df.info())
    print(df.describe())


def plot_faculty_titles_distribution(df):
    """
    Plot a combined chart showcasing faculty titles distribution.
    Left: Horizontal bar chart.
    Right: Donut chart.
    :param df: Input dataframe.
    """
    title_counts = df['Title'].value_counts()

    # Define grid specs and create the figure
    gs = gridspec.GridSpec(1, 2, width_ratios=[1.5, 1])
    fig = plt.figure(figsize=(18, 9))

    ax1 = plt.subplot(gs[0])  # Bar chart
    ax2 = plt.subplot(gs[1])  # Donut chart

    # --- Bar Chart ---
    sns.barplot(y=title_counts.index, x=title_counts.values, palette="viridis", ax=ax1)
    ax1.set_title('Faculty Titles Count')
    ax1.set_xlabel('Number of Faculty')
    ax1.set_ylabel('Title')

    # --- Donut Chart ---
    colors = sns.color_palette('pastel', len(title_counts))
    wedges, texts, autotexts = ax2.pie(title_counts,
                                       autopct='',
                                       startangle=140,
                                       wedgeprops=dict(width=0.3),
                                       textprops=dict(color="black"),
                                       colors=colors)

    # Draw a circle in the center for 'donut' style
    centre_circle = plt.Circle((0, 0), 0.70, fc='white')
    ax2.add_artist(centre_circle)

    # Add percentage labels outside the donut
    for i, (wedge, percentage) in enumerate(zip(wedges, title_counts / title_counts.sum() * 100)):
        ang = (wedge.theta2 - wedge.theta1) / 2. + wedge.theta1
        y = np.sin(np.deg2rad(ang))
        x = np.cos(np.deg2rad(ang))
        horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
        connectionstyle = f"angle,angleA=0,angleB={ang}"
        kwargs = dict(xycoords="data", textcoords="data", arrowprops=dict(arrowstyle="-", color="0.5",
                                                                          connectionstyle=connectionstyle), fontsize=10,
                      ha=horizontalalignment)
        ax2.annotate(f"{percentage:.1f}%", xy=(x, y), xytext=(1.7 * np.sign(x), 2 * y), **kwargs)

    # Beautify
    ax2.legend(title_counts.index, title='Titles', loc='upper left', bbox_to_anchor=(1.3, 0.9))
    ax2.set_title('Faculty Titles Percentage')

    fig.suptitle('Faculty Titles Distribution', fontsize=24, fontweight='bold')
    plt.tight_layout()

    # Save the figure to a file before displaying it
    fig.savefig('visualization/Faculty_Titles_Distribution.png', dpi=300, bbox_inches='tight')
    plt.show()


def clean_research_interests_data(df):
    """
     Helper function to clean research interests data.
    """

    def clean_interests(interest):
        # Removing characters like [, ], ', "
        cleaned = re.sub(r"[\'\"\[\]]", "", interest)

        # Taking only the main interest before phrases like "e.g."
        main_interest = cleaned.split(", e.g.")[0].strip()
        return main_interest.lower()  # Convert to lowercase

    # Splitting, cleaning and counting research interests
    research_interests = df['Research Interest'].str.split(',').explode().apply(clean_interests).str.strip()

    # Filtering out empty strings, NaN values, and strings like "e.g."
    valid_interests = research_interests[
        research_interests.notna() & (research_interests != '') & (~research_interests.str.contains("^e\.g\.$"))]

    return valid_interests


def plot_research_interests_distribution(df):
    """
    Plot an enhanced combined chart showcasing the top research interests.
    Includes a bar chart for the top 10 interests, a pie chart for the top 6, and a word cloud for all interests.
    """
    # Preparing data
    all_interests = clean_research_interests_data(df).tolist()
    interests_df = pd.DataFrame(all_interests, columns=['Interest'])
    research_counts = interests_df['Interest'].value_counts()

    # Top 10 for bar chart
    top_10_interests = research_counts.head(10)

    # Top 6 for pie chart
    top_6_interests = research_counts.head(6)

    # Set up the figure and axes
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))

    # Bar chart with enhanced colors
    color_palette = sns.color_palette("husl", 10)  # Using a vibrant color palette
    sns.barplot(y=top_10_interests.index, x=top_10_interests.values, ax=ax1, palette=color_palette)
    ax1.set_title('Top 10 Research Interests')
    ax1.set_xlabel('Number of Mentions')
    ax1.set_ylabel('Research Interest')

    # Pie chart with shadow and explosion effect
    explode = (0.1, 0.1, 0.1, 0.1, 0.1, 0.1)
    wedges, texts, autotexts = ax2.pie(top_6_interests,
                                       labels=top_6_interests.index,
                                       startangle=140,
                                       colors=sns.color_palette('pastel', 6),
                                       explode=explode,
                                       shadow=True,
                                       autopct='',
                                       pctdistance=0.85)
    for i, p in enumerate(wedges):
        ang = (p.theta2 - p.theta1) / 2. + p.theta1
        y = np.sin(np.deg2rad(ang))
        x = np.cos(np.deg2rad(ang))
        horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
        connectionstyle = f"angle,angleA=0,angleB={ang}"
        kwargs = dict(xycoords="data", textcoords="data", arrowprops=dict(arrowstyle="-", color="0.5",
                                                                          connectionstyle=connectionstyle), fontsize=10,
                      ha=horizontalalignment)
        ax2.annotate(f"{top_6_interests[i] / sum(top_6_interests) * 100:.1f}%", xy=(x, y),
                     xytext=(1.2 * np.sign(x), 1.4 * y), **kwargs)
    ax2.set_title('Top 6 Research Interests Distribution')

    plt.tight_layout()
    fig.subplots_adjust(top=0.82)
    fig.suptitle('Faculty Research Interests Distribution', fontsize=24, fontweight='bold')

    # Save the figure to a file before displaying it
    fig.savefig('visualization/Faculty_Research_Interests_Distribution.png', dpi=300, bbox_inches='tight')
    plt.show()


def plot_faculty_ages_distribution(df):
    """
    Plot histograms of graduate years and estimated ages side by side.
    """
    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(18, 7))

    # Plotting Graduate Year
    sns.histplot(df['Graduate Year'].dropna(), bins=30, kde=False, color="skyblue", ax=axes[0])
    axes[0].set_title('Timeline of Faculty Graduate Years')
    axes[0].set_xlabel('Graduate Year')
    axes[0].set_ylabel('Number of Faculty')

    # Plotting Estimated Age
    sns.histplot(df['Estimated age'].dropna(), bins=30, kde=True, color="dodgerblue", ax=axes[1])
    axes[1].axvline(df['Estimated age'].mean(), color='k', linestyle='--')
    axes[1].axvline(df['Estimated age'].median(), color='r', linestyle='-')
    axes[1].legend({'KDE': "dodgerblue", 'Mean Age': 'k--', 'Median Age': 'r-'})
    axes[1].set_title('Distribution of Faculty Estimated Ages')
    axes[1].set_xlabel('Estimated Age')
    axes[1].set_ylabel('Number of Faculty')

    plt.tight_layout()
    fig.subplots_adjust(top=0.82)
    fig.suptitle('Faculty Ages Distribution', fontsize=24, fontweight='bold')

    # Save the figure to a file before displaying it
    fig.savefig('visualization/Faculty_Ages_Distribution.png', dpi=300, bbox_inches='tight')
    plt.show()


def plot_faculty_department_and_title_distribution(df):
    """
    Plot a combined chart showcasing department distribution and title distribution within departments.
    Left: Horizontal bar chart of department distribution.
    Right: Grouped bar chart of title distribution within departments.
    """
    department_counts = df['Thrust/Department/Division'].value_counts()
    data_agg = df.groupby(['Thrust/Department/Division', 'Title']).size().reset_index(name='Counts')
    data_pivot = data_agg.pivot(index='Thrust/Department/Division', columns='Title', values='Counts').fillna(0)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10), gridspec_kw={'width_ratios': [1, 2]})

    # --- Bar Chart for Department Distribution ---
    color_palette = sns.color_palette("husl", len(department_counts))
    sns.barplot(y=department_counts.index, x=department_counts.values, palette=color_palette, ax=ax1)
    ax1.set_title('Department Distribution')
    ax1.set_xlabel('Number of Faculty')
    ax1.set_ylabel('Department')

    # --- Grouped Bar Chart for Title Distribution within Departments ---
    data_pivot.plot(kind='bar', stacked=True, ax=ax2, colormap="Set3")
    ax2.set_title('Title Distribution within Departments')
    ax2.set_ylabel('Number of Faculty')
    ax2.set_xlabel('Department')
    ax2.set_xticklabels(ax2.get_xticklabels(), rotation=45, ha='right')

    # Adjusting legend
    handles, labels = ax2.get_legend_handles_labels()
    ax2.legend(handles, labels, title='Title', loc='upper left', bbox_to_anchor=(1.05, 1))

    plt.tight_layout()
    fig.subplots_adjust(top=0.86)
    fig.suptitle('Faculty Department and Title Distribution', fontsize=24, fontweight='bold')

    # Save the figure to a file before displaying it
    fig.savefig('visualization/Faculty_Department_and_Title_Distribution.png', dpi=300, bbox_inches='tight')
    plt.show()


def plot_faculty_overview_word_cloud(df):
    """
    Plot combined word clouds showcasing common words in faculty research interests and overviews.
    """
    # Preparing data for research interests word cloud
    all_interests = clean_research_interests_data(df).tolist()
    interests_df = pd.DataFrame(all_interests, columns=['Interest'])
    research_counts = interests_df['Interest'].value_counts()

    # Generating research interests word cloud
    research_wordcloud = WordCloud(width=450,
                                   height=450,
                                   background_color='white',
                                   colormap="plasma",
                                   max_words=200,
                                   contour_width=3,
                                   contour_color='plasma').generate_from_frequencies(research_counts)

    # Preparing data for faculty overviews word cloud
    overview_text = ' '.join(df['Overview'].dropna())

    # Generating faculty overviews word cloud
    overview_wordcloud = WordCloud(background_color='white', width=450, height=450, max_words=100,
                                   colormap="viridis").generate(overview_text)

    # Setting up the figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 9))

    ax1.imshow(research_wordcloud, interpolation='bilinear')
    ax1.axis('off')
    ax1.set_title('Research Interests')

    ax2.imshow(overview_wordcloud, interpolation='bilinear')
    ax2.axis('off')
    ax2.set_title('Faculty Overviews')

    plt.suptitle('Word Clouds for Research Interests & Faculty Overviews', fontsize=24, fontweight='bold', y=1.05)
    plt.tight_layout()
    fig.subplots_adjust(top=0.86)
    fig.suptitle('Faculty Overview WordCloud', fontsize=24, fontweight='bold')

    # Save the figure to a file before displaying it
    fig.savefig('visualization/Faculty_Overview_WordCloud.png', dpi=300, bbox_inches='tight')
    plt.show()


if __name__ == '__main__':
    faculty_table, faculty_grad_year = load_data()

    # Perform basic exploratory data analysis
    print("Basic EDA for Faculty Table:")
    basic_eda(faculty_table)

    print("\nBasic EDA for Faculty Graduate Year:")
    basic_eda(faculty_grad_year)

    # visualizations
    plot_faculty_overview_word_cloud(faculty_table)
    plot_faculty_titles_distribution(faculty_table)
    plot_research_interests_distribution(faculty_table)
    plot_faculty_ages_distribution(faculty_grad_year)
    plot_faculty_department_and_title_distribution(faculty_table)
