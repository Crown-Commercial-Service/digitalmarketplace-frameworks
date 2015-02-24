var fs = require('fs');
var yaml = require("js-yaml");
var yamlJS = require("yamljs");
var walk = function(dir, done) {
  var results = [];
  fs.readdir(dir, function(err, list) {
    if (err) return done(err);
    var i = 0;
    (function next() {
      var file = list[i++];
      if (!file) return done(null, results);
      file = dir + '/' + file;
      fs.stat(file, function(err, stat) {
        if (stat && stat.isDirectory()) {
          walk(file, function(err, res) {
            results = results.concat(res);
            next();
          });
        } else {
          results.push(file);
          next();
        }
      });
    })();
  });
};

var i = 0;
var pages = []

walk("service", function(error, results) {
  results.forEach(function(file) {

    fs.readFile(file, 'utf8', function(error, data) {

      var page = yaml.safeLoad(data);

      Object.keys(page).forEach(function(pageKey) {

        console.log(
          "- Page " + ++i + "\n    name: " + pageKey + "\n    questions: "
        );
        pages.push(i);

        Object.keys(page[pageKey]).forEach(function(pageTitleAsKey) {
          var filename = page[pageKey][pageTitleAsKey].key + ".yml";
          console.log("        - " + filename);
          page[pageKey][pageTitleAsKey].question = pageTitleAsKey;
          delete page[pageKey][pageTitleAsKey].key;
          var content = yamlJS.stringify(page[pageKey][pageTitleAsKey], 4);
          //console.log(content);
          fs.writeFile("g6/" + filename, content, function(err) {
            //console.log("WRITTEN!");
          });
        });

      });

    });

  });

});
