import requests
from bs4 import BeautifulSoup
import lighthouse
import time

# ----------------------------
# Helper Functions
# ----------------------------

def fetch_page_content(url):
    """Fetches the HTML content of the landing page."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the page: {e}")
        return None


def analyze_lighthouse(url):
    """Runs Lighthouse audit and returns UX, SEO, Performance scores."""
    try:
        # Run Lighthouse audit
        results = lighthouse.run(
            url,
            [
                "performance",
                "seo",
                "accessibility"
            ],
            chrome_flags="--headless"
        )

        # Extract scores
        accessibility_score = results["categories"]["accessibility"]["score"] * 100
        seo_score = results["categories"]["seo"]["score"] * 100
        performance_score = results["categories"]["performance"]["score"] * 100

        return {
            "ux_score": accessibility_score,
            "seo_score": seo_score,
            "performance_score": performance_score,
            "audit_results": results
        }
    except Exception as e:
        print(f"Lighthouse audit failed: {e}")
        return None


def get_performance_metrics(results):
    """Extracts mobile and desktop performance metrics from Lighthouse results."""
    try:
        fcp = results["audits"]["first-contentful-paint"]["displayValue"]
        speed_index = results["audits"]["speed-index"]["displayValue"]
        tti = results["audits"]["interactive"]["displayValue"]

        return {
            "first_contentful_paint": fcp,
            "speed_index": speed_index,
            "time_to_interactive": tti
        }
    except KeyError as e:
        print(f"Missing metric in Lighthouse report: {e}")
        return {}


def generate_heatmap_suggestions():
    """Provides basic heatmap suggestions based on best practices."""
    return [
        "Place CTAs above the fold.",
        "Highlight key features in the middle section.",
        "Minimize distractions around important elements.",
        "Use contrasting colors for buttons and links.",
        "Ensure forms are short and easy to fill."
    ]


# ----------------------------
# Main Analyzer Function
# ----------------------------

def analyze_landing_page(url):
    """Analyzes a landing page URL and returns UX, SEO, performance, and heatmap insights."""
    print(f"\n🔍 Analyzing landing page: {url}\n")

    # Step 1: Fetch page content
    html_content = fetch_page_content(url)
    if not html_content:
        return None

    # Step 2: Run Lighthouse audit
    lighthouse_data = analyze_lighthouse(url)
    if not lighthouse_data:
        return None

    # Step 3: Extract performance metrics
    perf_metrics = get_performance_metrics(lighthouse_data["audit_results"])

    # Step 4: Generate heatmap suggestions
    heatmap_suggestions = generate_heatmap_suggestions()

    # Step 5: Compile final report
    analysis_report = {
        "url": url,
        "ux_score": round(lighthouse_data["ux_score"], 2),
        "seo_score": round(lighthouse_data["seo_score"], 2),
        "performance_score": round(lighthouse_data["performance_score"], 2),
        "performance_metrics": perf_metrics,
        "heatmap_suggestions": heatmap_suggestions
    }

    return analysis_report


# ----------------------------
# CLI Runner
# ----------------------------

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python landing_page_analyzer.py [URL]")
        sys.exit(1)

    target_url = sys.argv[1]
    start_time = time.time()

    result = analyze_landing_page(target_url)

    end_time = time.time()
    duration = round(end_time - start_time, 2)

    if result:
        print("\n✅ Analysis Complete!\n")
        print(f"🌐 URL: {result['url']}")
        print(f"🧩 UX Score: {result['ux_score']}%")
        print(f"🔍 SEO Score: {result['seo_score']}%")
        print(f"⚡ Performance Score: {result['performance_score']}%")
        print("\n⏱️ Key Performance Metrics:")
        print(f"- First Contentful Paint: {result['performance_metrics'].get('first_contentful_paint', 'N/A')}")
        print(f"- Speed Index: {result['performance_metrics'].get('speed_index', 'N/A')}")
        print(f"- Time to Interactive: {result['performance_metrics'].get('time_to_interactive', 'N/A')}")
        print("\n📌 Heatmap Suggestions:")
        for i, suggestion in enumerate(result['heatmap_suggestions'], 1):
            print(f"{i}. {suggestion}")
        print(f"\n⏱️ Total Execution Time: {duration} seconds")
    else:
        print("❌ Failed to analyze the landing page.")