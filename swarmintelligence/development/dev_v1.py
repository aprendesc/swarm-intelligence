from eigenlib.LLM.web_parser import WebParserClass
parser = WebParserClass("https://es.wikipedia.org/wiki/Lockheed_Martin_F-22_Raptor")
content = parser.run()
