import mechanize
import netifaces
import base64
import optparse
import sys
from bs4 import BeautifulSoup # pip install BeautifulSoup4

if __name__ == '__main__':

    url = "http://wsprnet.org/drupal/wsprnet/spotquery"
    print "Wsprnet.org results parser v1.0"
    print "Run 'python wspr_stat.py --callsign=XXXXXX [--reporter=YYYYYY] [--count=50] [--band=Band] [--time=Time]' where"
    print "    Band: All, 1, 3, 5, 7, 10, 14, 18, 21, 24, 28, 50, 70, 144, 432, 1296"
    print "    Time: 3600, 43200, 86400, 604800, 1209600"
    print "Warning: all data is unofficial"
    print ""

    parser = optparse.OptionParser()
    parser.add_option("--callsign", dest="callsign", help="callsign", default="")
    parser.add_option("--reporter", dest="reporter", help="reporter", default="")
    parser.add_option("--band", dest="band", help="values in report", default="All")
    parser.add_option("--count", dest="count", help="values in report", default="50")
    parser.add_option("--time", dest="timeLimit", help="time in seconds", default="3600")
    options, args = parser.parse_args()
    
    callsign = options.callsign
    reporter = options.reporter
    band  = options.band
    count = options.count
    timeLimit = options.timeLimit

    if len(callsign) == 0 and len(reporter) == 0:
        print "Error: you need to specify callsign of sender or reporter"
        sys.exit(0)
    
    print "Callsign:", callsign if len(callsign) > 0 else "-"
    print "Reporter:", reporter if len(reporter) > 0 else "-"
    print "Report count:", count
    print "Time limit:", timeLimit
    print "Band:", band
    print ""

    print "Making request..."
    br = mechanize.Browser()
    try:
        #br.set_handle_equiv(True)
        #br.set_debug_redirects(True)
        #br.set_debug_responses(True)
        br.set_handle_robots(False)
        br.set_handle_redirect(True)
        #br.set_handle_referer(True)
        #br.set_debug_http(True)
        br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
        
        br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=10)

        br.open(url)
        # Find proper form
        nr = 0
        for idx, f in enumerate(br.forms()):
          if f.attrs["id"] == "wsprnet-spotquery-form":
              nr = idx
        br.select_form(nr=nr)
        br.form.set_all_readonly(False)

        #print "Available controls:"
        #for c in br.form.controls:
        #     print "  ", c
        #print ""

        # Set fields
        br.form['count'] = count
        br.form['call'] = callsign
        br.form['reporter'] = reporter
        # <SelectControl(band=[*All, -1, 0, 1, 3, 5, 7, 10, 14, 18, 21, 24, 28, 50, 70, 144, 432, 1296])>
        br.form['band'] = [ band ]
        # <SelectControl(timelimit=[3600, 43200, 86400, 604800, 1209600])>
        br.form['timelimit'] = [ timeLimit ]
        # <SelectControl(sortby=[*date, callsign, reporter, mhz, db, power, distance, grid, distance/pow(10,(power-30.0)/10.0)])>
        br.form['sortby'] = [ 'date' ]
        response = br.submit()
        resultStr = response.read()
        
        soup = BeautifulSoup(resultStr, "html.parser")
        table = soup.find("table")
        
        def filter(text):
            return ''.join(i for i in text if ord(i)<128)

        print ""
        count = 0
        for row in table.find_all('tr'):
            td_tags = row.find_all('td')
            if len(td_tags) >= 11:
                timestamp = filter(td_tags[0].text)
                call = filter(td_tags[1].text)
                mhz = filter(td_tags[2].text)
                snr = filter(td_tags[3].text)
                drift = filter(td_tags[4].text)
                grid = filter(td_tags[5].text)
                pwr = filter(td_tags[6].text)
                reporter = filter(td_tags[7].text)
                rgrid = filter(td_tags[8].text)
                km = filter(td_tags[9].text)
                az = filter(td_tags[10].text)
                print "{}: {}, reported by {} ({}), SNR:{}, dist:{}km, Az:{}".format(timestamp, call, reporter, grid, snr, km, az)
                count += 1
        print "{} items found".format(count)

    except Exception, e:
      print "Error:", str(e)

    print "Done"
