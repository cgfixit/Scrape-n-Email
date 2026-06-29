# Offline unit tests for the parse_* functions of the three scrapers.
#
# These exercise the parsing logic against representative HTML fixtures with NO
# network access, so they run anywhere (incl. CI / blocked-network sandboxes).
# Live selector confirmation still requires reaching the real sites.
#
# Run:  python -m unittest test_scrapers -v   (or: python test_scrapers.py)

import datetime
import unittest

from scrape_n_email.scrapers import clist as clistScraper  # noqa: N812
from scrape_n_email.scrapers import drudge as drudgeScraper
from scrape_n_email.scrapers import rcp as rcpScraper  # noqa: N812

CRAIGSLIST_HTML = """
<html><body>
  <ul>
    <li class="cl-static-search-result" title="Senior Network Engineer">
      <a href="https://atlanta.craigslist.org/nat/sad/d/atlanta-senior-network-engineer/7777777777.html">
        <div class="title">Senior Network Engineer</div>
        <div class="details">
          <div class="price">$120,000</div>
          <div class="location">Buckhead</div>
        </div>
      </a>
    </li>
    <li class="cl-static-search-result" title="Linux Sysadmin">
      <a href="https://atlanta.craigslist.org/atl/sad/d/atlanta-linux-sysadmin/8888888888.html">
        <div class="title">Linux Sysadmin</div>
        <div class="details"><div class="location">Midtown</div></div>
      </a>
    </li>
    <li class="cl-static-search-result" title="No Link Bogus">
      <a>Broken entry without href</a>
    </li>
  </ul>
</body></html>
"""

DRUDGE_HTML = """
<html><body>
  <center>
    <b><a href="https://bignews.example.com/splash-story-of-the-day">SPLASH HEADLINE OF THE DAY</a></b>
  </center>
  <table><tr>
    <td><a href="https://left.example.com/story-one">Left column long headline one</a></td>
    <td><a href="https://center.example.com/story-two">Center column long headline two</a></td>
    <td><a href="https://right.example.com/story-three">Right column long headline three</a></td>
  </tr></table>
  <a href="https://twitter.com/drudge">Follow</a>
  <a href="https://www.drudgereport.com/privacy.htm">PRIVACY POLICY</a>
  <a href="https://left.example.com/story-one">Left column long headline one</a>
  <a href="https://x.com/short">hi</a>
  <a href="https://netflix.com/news/streaming-wars-heat-up-again">Streaming Wars Heat Up Again Nationwide</a>
  <a href="https://news.example.com/about-face-on-tariffs-today">Major About Face On Tariffs Announced</a>
</body></html>
"""

# RCP page where a container exists but its link is NOT article-shaped; the
# only scrapeable headline is reachable solely via the full-page fallback.
RCP_SHADOW_HTML = """
<html><body>
  <div class="story">
    <a href="https://external.example.com/oped-no-pattern">Some Op-Ed With A Long Title Here</a>
  </div>
  <a href="/articles/2026/06/06/real_fallback_story_777.html">Real Fallback Story Worth Reading</a>
</body></html>
"""

RCP_HTML = """
<html><body>
  <div class="trending-headlines">
    <a href="/articles/2026/06/06/the_big_political_story_151515.html">The Big Political Story Today</a>
    <a href="/video/2026/06/05/some_video_clip_999.html">Watch: Some Video Clip Here</a>
  </div>
  <div class="story">
    <a href="https://www.realclearpolitics.com/articles/2026/06/04/another_headline_222.html">Another Headline Worth Reading</a>
  </div>
  <a href="/about.html">About</a>
  <a href="https://twitter.com/rcp">Follow us</a>
  <a href="/articles/2026/06/06/the_big_political_story_151515.html">The Big Political Story Today</a>
</body></html>
"""


class CraigslistTests(unittest.TestCase):
    def setUp(self):
        self.jobs = clistScraper.parse_jobs(CRAIGSLIST_HTML)

    def test_count_and_skips_broken(self):
        # 2 valid listings; the href-less <li> is dropped.
        self.assertEqual(len(self.jobs), 2)

    def test_fields_extracted(self):
        first = self.jobs[0]
        self.assertEqual(first["title"], "Senior Network Engineer")
        self.assertEqual(first["price"], "$120,000")
        self.assertEqual(first["location"], "Buckhead")

    def test_links_absolute_not_mangled(self):
        # Regression guard for the old `domain + href` bug.
        for job in self.jobs:
            self.assertTrue(job["link"].startswith("https://atlanta.craigslist.org/"))
            self.assertNotIn("craigslist.com/https", job["link"])


class DrudgeTests(unittest.TestCase):
    def setUp(self):
        self.headlines = drudgeScraper.parse_headlines(DRUDGE_HTML)
        self.links = [h["link"] for h in self.headlines]

    def test_filters_social_self_and_short(self):
        self.assertNotIn("https://twitter.com/drudge", self.links)
        self.assertNotIn("https://www.drudgereport.com/privacy.htm", self.links)
        self.assertNotIn("https://x.com/short", self.links)

    def test_dedupes(self):
        self.assertEqual(len(self.links), len(set(self.links)))
        # splash + 3 columns + netflix + about-face look-alikes
        self.assertEqual(len(self.headlines), 6)

    def test_top_flag_for_bold(self):
        top = self.headlines[0]
        self.assertTrue(top["top"])
        self.assertEqual(top["source"], "bignews.example.com")

    def test_lookalike_domain_not_dropped(self):
        # Regression: 'netflix.com'.endswith('x.com') must NOT match _SKIP_HOSTS.
        self.assertIn("https://netflix.com/news/streaming-wars-heat-up-again", self.links)
        # The real social host is still filtered.
        self.assertNotIn("https://x.com/short", self.links)

    def test_path_segment_not_substring_dropped(self):
        # Regression: '/about-face-...' must survive (segment is 'about-face').
        self.assertIn("https://news.example.com/about-face-on-tariffs-today", self.links)


class RCPTests(unittest.TestCase):
    def setUp(self):
        self.headlines = rcpScraper.parse_headlines(RCP_HTML)
        self.links = [h["link"] for h in self.headlines]

    def test_relative_links_made_absolute(self):
        self.assertIn(
            "https://www.realclearpolitics.com/articles/2026/06/06/the_big_political_story_151515.html",
            self.links,
        )

    def test_filters_nav_and_social(self):
        self.assertFalse(any("/about.html" in link for link in self.links))
        self.assertFalse(any("twitter.com" in link for link in self.links))

    def test_dedupes_and_finds_articles(self):
        self.assertEqual(len(self.links), len(set(self.links)))
        self.assertEqual(len(self.headlines), 3)

    def test_lookalike_host_not_substring_dropped(self):
        # Regression: a syndicated article on netflix.com must not be dropped by
        # the 'x.com' social-host rule (old substring filter did exactly that).
        html = (
            '<html><body><a href="https://www.netflix.com/news/2026/doc.html">'
            "Streaming Documentary Sparks National Debate</a></body></html>"
        )
        links = [h["link"] for h in rcpScraper.parse_headlines(html)]
        self.assertIn("https://www.netflix.com/news/2026/doc.html", links)

    def test_falls_back_when_container_links_unusable(self):
        # Regression: a container exists but its link is not article-shaped;
        # the fallback must still find the real RCP article link.
        headlines = rcpScraper.parse_headlines(RCP_SHADOW_HTML)
        links = [h["link"] for h in headlines]
        self.assertIn(
            "https://www.realclearpolitics.com/articles/2026/06/06/real_fallback_story_777.html",
            links,
        )
        self.assertEqual(len(headlines), 1)


# ---------------------------------------------------------------------------
# Edge-case / robustness tests added to complement the baseline tests above.
# ---------------------------------------------------------------------------


class CraigslistEdgeTests(unittest.TestCase):
    def test_empty_html_returns_empty_list(self):
        self.assertEqual(clistScraper.parse_jobs(""), [])

    def test_none_html_returns_empty_list(self):
        self.assertEqual(clistScraper.parse_jobs(None), [])

    def test_limit_enforced(self):
        jobs = clistScraper.parse_jobs(CRAIGSLIST_HTML, limit=1)
        self.assertEqual(len(jobs), 1)

    def test_missing_price_defaults_to_empty_string(self):
        # The Linux Sysadmin fixture has no price node.
        jobs = clistScraper.parse_jobs(CRAIGSLIST_HTML)
        sysadmin = next(j for j in jobs if j["title"] == "Linux Sysadmin")
        self.assertEqual(sysadmin["price"], "")

    def test_duplicate_links_deduped(self):
        # Inject a second copy of the first listing with the same href.
        dup_html = (
            CRAIGSLIST_HTML
            + """
        <ul>
          <li class="cl-static-search-result" title="Senior Network Engineer Dup">
            <a href="https://atlanta.craigslist.org/nat/sad/d/atlanta-senior-network-engineer/7777777777.html">
              <div class="title">Senior Network Engineer (duplicate)</div>
            </a>
          </li>
        </ul>"""
        )
        jobs = clistScraper.parse_jobs(dup_html)
        links = [j["link"] for j in jobs]
        self.assertEqual(len(links), len(set(links)))

    def test_bytes_input_accepted(self):
        # BeautifulSoup handles bytes; parse_jobs must not raise.
        jobs = clistScraper.parse_jobs(CRAIGSLIST_HTML.encode("utf-8"))
        self.assertEqual(len(jobs), 2)


class DrudgeEdgeTests(unittest.TestCase):
    def test_empty_html_returns_empty_list(self):
        self.assertEqual(drudgeScraper.parse_headlines(""), [])

    def test_none_html_returns_empty_list(self):
        self.assertEqual(drudgeScraper.parse_headlines(None), [])

    def test_all_social_filtered_returns_empty(self):
        html = (
            "<html><body>"
            '<a href="https://twitter.com/drudge">Follow us on Twitter here</a>'
            '<a href="https://x.com/drudge">Follow us on X platform now</a>'
            "</body></html>"
        )
        self.assertEqual(drudgeScraper.parse_headlines(html), [])

    def test_non_bold_link_not_top(self):
        # Links outside bold/strong/red-font markup must have top=False.
        headlines = drudgeScraper.parse_headlines(DRUDGE_HTML)
        non_top = [h for h in headlines if not h["top"]]
        self.assertGreater(len(non_top), 0)

    def test_limit_enforced(self):
        headlines = drudgeScraper.parse_headlines(DRUDGE_HTML, limit=2)
        self.assertLessEqual(len(headlines), 2)


class RCPEdgeTests(unittest.TestCase):
    def test_empty_html_returns_empty_list(self):
        self.assertEqual(rcpScraper.parse_headlines(""), [])

    def test_none_html_returns_empty_list(self):
        self.assertEqual(rcpScraper.parse_headlines(None), [])

    def test_bytes_input_accepted(self):
        headlines = rcpScraper.parse_headlines(RCP_HTML.encode("utf-8"))
        self.assertEqual(len(headlines), 3)

    def test_limit_enforced(self):
        headlines = rcpScraper.parse_headlines(RCP_HTML, limit=1)
        self.assertLessEqual(len(headlines), 1)

    def test_source_strips_www(self):
        # Sources should have www. stripped for cleaner display.
        headlines = rcpScraper.parse_headlines(RCP_HTML)
        for h in headlines:
            self.assertFalse(h["source"].startswith("www."), h["source"])

    def test_next_year_url_recognized_as_headline(self):
        # Regression: _CONTENT_HINTS must match next-year article URLs so the
        # filter keeps working across the year boundary without a code change.
        next_year = datetime.date.today().year + 1
        html = (
            f'<html><body>'
            f'<a href="https://www.realclearpolitics.com/articles/{next_year}/'
            f'01/01/headline_story_worth_reading.html">'
            f'Important Breaking Headline Worth Reading Here</a>'
            f'</body></html>'
        )
        headlines = rcpScraper.parse_headlines(html)
        self.assertGreater(len(headlines), 0, f"/{next_year}/ URL not matched by _CONTENT_HINTS")
