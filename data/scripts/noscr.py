"""
Analyzes the uses of the noscript tag.
"""
from util import get_paths, parse_csv_line, as_bool
from util import benchmark_columns as columns

from urllib.parse import urlparse
import os
import lxml.html

bm_file_path, _, noscript_dir_path, _ = get_paths()

# Category definitions.
cat_alt = "alternative_content"
cat_track = "tracking_metrics"
cat_other = "other"

def warn_tag(tag, url):
    """
    Warns about a tag not being recognized properly.
    """
    print("Unrecognized tag for {}: {} {}".format(url.hostname, tag.tag, tag.attrib))

def is_url_relative(url):
    """
    True if a URL is relative, False otherwise.
    """
    return url[0] == "/" and url[1] != "/"

def one_of_in(lst, val):
    """
    Returns True if one of the items in the given list exists
    in the given value, False otherwise.
    """
    for l in lst:
        if l in val:
            return True
    
    return False

def process_iframe(tag, url):
    """
    Handler for iframe tags.
    """
    iframe_src = tag.get("src")

    if iframe_src is not None:
        # Google Tag Manager
        if "googletagmanager.com" in iframe_src:
            return [( cat_track, "google_tag_manager" )]
        
        # Google Analytics
        if "google-analytics.com" in iframe_src:
            return [( cat_track, "google_analytics" )]
        
        # DoubleClick
        if "fls.doubleclick.net" in iframe_src:
            return [( cat_track, "doubleclick" )]
        
        # TheBrightTag
        if "thebrighttag.com" in iframe_src:
            return [( cat_track, "the_bright_tag" )]
        
        # Relative framed content
        if is_url_relative(iframe_src):
            return [( cat_alt, "frame_content" )]
    
    return None

def process_style(tag, url):
    """
    Handler for style tags.
    """
    return [( cat_alt, "inline_style" )]

def process_link(tag, url):
    """
    Handler for link tags.
    """
    link_rel = tag.get("rel")
    link_type = tag.get("type")
    link_href = tag.get("href")

    # Stylesheet
    if link_rel == "stylesheet" or link_type == "text/css":
        return [( cat_alt, "stylesheet" )]
    
    # Google Fonts
    if link_rel == "preload" and "fonts.googleapis.com" in link_href:
        return [( cat_alt, "stylesheet" )]

def process_picture(tag, url):
    """
    Handler for picture tags.
    """
    # Only present in Jimdo
    return [( cat_alt, "static_content" )]

def process_meta(tag, url):
    """
    Handler for meta tags.
    """
    meta_http_equiv = tag.get("http-equiv")

    # Meta refresh
    if meta_http_equiv is not None and meta_http_equiv.lower() == "refresh":
        return [( cat_other, "refresh" )]
    else:
        return [( cat_other, "meta_content" )]

def process_a(tag, url):
    """
    Handler for a tags.
    """
    return [( cat_alt, "link" )]

def process_video(tag, url):
    """
    Handler for video tags.
    """
    return [( cat_alt, "video" )]

def process_noop(tag, url):
    """
    Handler for tags that don't contain meaningful information.
    """
    return []

def process_text(tag, url):
    """
    Handler for tags that might contain text content.
    """
    if len(tag.text_content().strip()) > 0:
        return [( cat_alt, "text" )]
    
    return None

def process_container(tag, url):
    """
    Handler for tags that have other tags as children.
    """
    tag_children = tag.findall("*")
    tag_results = []

    for tag_child in tag_children:
        tag_result = process_tag(tag_child, url)

        if tag_result is not None:
            tag_results.extend(tag_result)
        else:
            warn_tag(tag, url)
    
    return tag_results

def process_div(tag, url):
    """
    Handler for div tags.
    """
    div_class = tag.get("class")

    if div_class is not None:
        # StatCounter
        if "statcounter" in div_class:
            return [( cat_track, "statcounter" )]

        # WebMD
        if "global-footer-certificates" in div_class:
            return [( cat_alt, "static_content" )]

        # BBC
        if "top-story__image" in div_class:
            return [( cat_alt, "static_content" )]
        
        # EBay
        if "hl-image" in div_class:
            return [( cat_alt, "static_content" )]
    
    # Try it with text content.
    r = process_text(tag, url)

    if r is not None:
        return r
    
    # Try it with its children.
    return process_container(tag, url)

def process_img(tag, url):
    # Shopify uses srcset and is the only website to do so iirc
    if tag.get("srcset") is not None:
        if "shopify.com" in url.netloc:
            return [( cat_alt, "static_content" )]
    
    img_src = tag.get("src")

    if img_src is not None:
        # Scorecard
        if "b.scorecardresearch.com" in img_src:
            return [( cat_track, "scorecard_research" )]
        
        # Facebook
        if "facebook.com/tr" in img_src:
            return [( cat_track, "facebook" )]
        
        # Pinterest
        if "ct.pinterest.com" in img_src:
            return [( cat_track, "pinterest" )]
        
        # IMR Worldwide
        if "imrworldwide.com" in img_src:
            return [( cat_track, "imr_worldwide" )]
        
        # Google Ad Conversion
        if "googleadservices.com/pagead/conversion" in img_src:
            return [( cat_track, "google_ad_conversion" )]
        
        # LinkedIn
        if "ads.linkedin.com/collect" in img_src:
            return [( cat_track, "linkedin" )]
        
        # Microsoft
        if "web.vortex.data.microsoft.com" in img_src:
            return [( cat_track, "microsoft" )]
        
        # TNS Counter
        if "tns-counter.ru" in img_src:
            return [( cat_track, "tns_counter" )]
        
        # Quantcast
        if "pixel.quantserve.com" in img_src:
            return [( cat_track, "quantcast" )]
        
        # Twitter
        if "analytics.twitter.com" in img_src or "t.co/i/adsct" in img_src:
            return [( cat_track, "twitter" )]
        
        # ABC.ES
        if "rrss.abc.es/pixel" in img_src:
            return [( cat_track, "abc_es" )]
        
        # AdForm
        if "adform.net/Serving/TrackPoint" in img_src:
            return [( cat_track, "adform" )]
        
        # Bing Conversion
        if "bat.bing.com" in img_src:
            return [( cat_track, "bing" )]
        
        # DoubleClick
        if "doubleclick.net/pagead" in img_src or "ad.doubleclick.net" in img_src:
            return [( cat_track, "doubleclick" )]
        
        # Google Analytics
        if "google-analytics.com" in img_src:
            return [( cat_track, "google_analytics" )]
        
        # Quora
        if "quora.com/_/ad" in img_src:
            return [( cat_track, "quora" )]
        
        # Amazon
        if "fls-na.amazon.com" in img_src:
            return [( cat_track, "amazon" )]
        
        # BBC
        if "ssc.api.bbc.com" in img_src or "api.bbc.co.uk" in img_src:
            return [( cat_track, "bbc" )]
        
        # EFF
        if "anon-stats.eff.org" in img_src:
            return [( cat_track, "eff" )]
        
        # Taboola
        if "trc.taboola.com" in img_src:
            return [( cat_track, "taboola" )]
        
        # Wordpress
        if "pixel.wp.com" in img_src:
            return [( cat_track, "wordpreess" )]
        
        # Bizographics
        if "bizographics.com/collect" in img_src:
            return [( cat_track, "bizographics" )]
        
        # Buzzfeed
        if "pixiedust.buzzfeed.com" in img_src:
            return [( cat_track, "buzzfeed" )]
        
        # El Mundo
        if "smetrics.el-mundo.net" in img_src:
            return [( cat_track, "el_mundo" )]
        
        # Ziff Davis
        if "zdbb.net/l" in img_src:
            return [( cat_track, "ziff_davis" )]

        # Guardian
        if "phar.gu-web.net" in img_src:
            return [( cat_track, "the_guardian" )]
        
        # Timeout
        if "smetrics.timeout.com" in img_src:
            return [( cat_track, "timeout")]
        
        # Amazon Cloudfront
        if "cloudfront.net/atrk.gif" in img_src:
            return [( cat_track, "amazon_cloudfront" )]
        
        # Rambler
        if "counter.rambler.ru" in img_src:
            return [( cat_track, "rambler" )]
        
        # Yandex
        if "mc.yandex.ru" in img_src or "yabs.yandex.ru" in img_src:
            return [( cat_track, "yandex" )]
        
        # Mail.ru
        if "r3.mail.ru" in img_src or "mail.ru/counter" in img_src:
           return [( cat_track, "mail_ru" )]
        
        # XiTi
        if "xiti.com" in img_src:
            return [( cat_track, "xiti" )]
        
        # Archive
        if "analytics.archive.org" in img_src:
            return [( cat_track, "archive" )]
        
        # Financial Times
        if "ft.com/px.gif" in img_src:
            return [( cat_track, "financial_times" )]
        
        # Adobe Digital Marketing
        if "omtrdc.net" in img_src:
            return [( cat_track, "adobe_digital_marketing" )]
        
        # Omniture
        if "2o7.net" in img_src or "2O7.net" in img_src:
            return [( cat_track, "omniture" )]
        
        # Matomo/Piwik
        if "analytics.ietf.org" in img_src or "athena.iubenda.com/js" in img_src or "piwik.itzbund.de" in img_src:
            return [( cat_track, "matomo_piwik" )]
        
        # Offerlogic
        if "saffron.760main.com/oll" in img_src:
            return [( cat_track, "offerlogic" )]

        # Rakuten
        if "rakuten.112.2O7.net" in img_src:
            return [( cat_track, "rakuten" )]

        # Alexa
        if "alexametrics.com/atrk.gif" in img_src:
            return [( cat_track, "alexa" )]
        
        # Spotify
        if "pixel.spotify.com" in img_src:
            return [( cat_track, "spotify" )]
        
        # Relative images
        if is_url_relative(img_src):
            return [( cat_alt, "static_content" )]
        
        # Lots of hosts
        if one_of_in([
            "i.ytimg.com",                      # Youtube thumbnails
            "s.w-x.co",                         # Wetter.de
            "googleusercontent.com",            # Google hosted
            "images.arcpublishing.com",         # The Globe And Mail
            "cloudfront.net/thumbnails",        # Thumbnail hosted on Cloudfront
            "wp-content/uploads",               # Wordpress uploads
            "imageserver/image",                # Times UK
            "images/thumb",                     # More thumbnails
            "springernature.com/springer-cms",  # Springer
            "imagesvc.meredithcorp.io",         # People
            "cdn.vox-cdn.com",                  # Vox
            "cdni.rt.com",                      # RT
            "www.theglobeandmail.com/resizer",  # The Globe And Mail (again)
        ], img_src):
            return [( cat_alt, "static_content" )]
        
        img_src_url = urlparse(img_src)

        # Hosted on CDNs
        if img_src_url.netloc.startswith("cdn") or img_src_url.netloc.startswith("img"):
            return [( cat_alt, "static_content" )]

        # More general rules for images
        if one_of_in([ "static", "cdn", img_src_url.netloc ], img_src):
            img_alt = tag.get("alt")
            
            # Image with alt text.
            if img_alt is not None and len(img_alt.strip()) > 0:
                return [( cat_alt, "static_content" )]
            
            img_class = tag.get("class")

            # Image with some class.
            if img_class is not None and len(img_class.strip()) > 0:
                return [( cat_alt, "static_content" )]
            
            img_width = tag.get("width")
            img_height = tag.get("height")

            # Visible image.
            if img_width is not None and img_height is not None:
                img_width = int(img_width)
                img_height = int(img_height)

                if img_width >= 64 and img_height >= 64:
                    return [( cat_alt, "static_content" )]
    
    return None

tag_dict = {

    "iframe":   process_iframe,
    "style":    process_style,
    "link":     process_link,
    "picture":  process_picture,
    "meta":     process_meta,
    "a":        process_a,
    "video":    process_video,
    "div":      process_div,
    "img":      process_img

}

# I got lazy.
def register_all(tag_lst, handler):
    for t in tag_lst:
        tag_dict[t] = handler

register_all([ "br", "label" ], process_noop)
register_all([ "h1", "h2", "h3", "h4", "h5", "h6", "em", "strong", "b", "i", "p", "figcaption", "form" ], process_text)
register_all([ "p", "td", "span" ], process_container)

def process_tag(tag, url):
    """
    Processes a tag by passing it to the according
    tag handler. Returns None if a tag handler doesn't exist
    or if the corresponding tag handler couldn't make sense of it.
    Otherwise returns a list of tuples that contain the category
    and a more specific description of the detected content.
    """
    tag_name = tag.tag
    tag_handler = tag_dict.get(tag_name, None)

    if tag_handler is None:
        return None
    else:
        return tag_handler(tag, url)

def process_noscript_tags(noscript_tags, url):
    """
    Special handler for list of noscript tags.
    """
    results = []

    for noscript_tag in noscript_tags:
        tags = noscript_tag.findall("*")

        if len(tags) == 0:
            results.append(( cat_other, "empty" ))
            continue
        
        for tag in tags:
            r = process_tag(tag, url)

            if r is not None:
                results.extend(r)
            else:
                warn_tag(tag, url)
    
    return results

def get_noscript_tags(file_path):
    """
    Returns a list of parsed noscript tags from the given
    file path, assuming that the file contains nothing but
    noscript elements in the document root.
    """
    return lxml.html.parse(file_path).find("body").findall("noscript")

with open(bm_file_path, "r") as f:
    # Skip CSV header
    next(f)

    results = {}
    pages_scanned = 0

    for line in f:
        # Scan line for both JS and no JS.
        row_js = parse_csv_line(line)
        row_no_js = parse_csv_line(next(f))

        noscript_tags = []
        url = urlparse(row_js[columns["url"]])

        # Check if page with JS enabled sent any noscript tags.
        if as_bool(row_js[columns["noscript"]]):
            file_path = os.path.join(noscript_dir_path, row_js[columns["dataFileName"]] + ".html")
            noscript_tags.extend(get_noscript_tags(file_path))
        
        # Check if page with JS disabled sent any noscript tags.
        if as_bool(row_no_js[columns["noscript"]]):
            file_path = os.path.join(noscript_dir_path, row_no_js[columns["dataFileName"]] + ".html")
            noscript_tags.extend(get_noscript_tags(file_path))
        
        if len(noscript_tags) > 0:
            print("Processing {}".format(url.hostname))

            r = process_noscript_tags(noscript_tags, url)
            pages_scanned += 1

            # Only keep unique results
            r = list(set(r))

            for cat, detail in r:
                # Check if category exists
                if cat not in results:
                    results[cat] = {}
                
                # Check if detailed description exists
                if detail not in results[cat]:
                    results[cat][detail] = 0
                
                results[cat][detail] += 1
    
    print()
    print("Pages scanned: {}".format(pages_scanned))
    print("Results:")

    for cat in results:
        print("\t{}".format(cat))

        details = sorted(results[cat].items(), key=lambda x: x[1], reverse=True)

        for d in details:
            print("\t\t{} ({})".format(d[0], d[1]))