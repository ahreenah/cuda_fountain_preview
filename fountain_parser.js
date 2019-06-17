 var fountain = require('fountain-js');
 
 string = process.argv[2]
 var output = fountain.parse(string);
 
 process.stdout.write(output['script_html'])