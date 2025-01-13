{
    "QuestionId": "WebQTest-0",
    "RawQuestion": "what does jamaican people speak?",
    "Sparql": "PREFIX ns: <http://rdf.freebase.com/ns/>\nSELECT DISTINCT ?x\nWHERE {\nFILTER (?x != ns:m.03_r3)\nFILTER (!isLiteral(?x) OR lang(?x) = '' OR langMatches(lang(?x), 'en'))\nns:m.03_r3 ns:location.country.languages_spoken ?x .\n}\n",
    "SExpr": "(JOIN (R location.country.languages_spoken) m.03_r3)"
        }