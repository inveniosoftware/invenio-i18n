/*
 * This file is part of Invenio.
 * Copyright (C) 2016-2018 CERN.
 * Copyright (C) 2016 TIND.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import angular from "angular";
import "angular-gettext/dist/angular-gettext";
import * as $ from "jquery/dist/jquery";

// TODO: Delete this ?
angular.module("langSelector", ["gettext"]).factory("setLanguage", [
  "gettextCatalog",
  function(gettextCatalog) {
    function setCurrentLanguage(lang) {
      gettextCatalog.setCurrentLanguage(lang);
    }
  }
]);

$(document).ready(function() {
  $("#lang-code").on("change", function() {
    $("#language-code-form").submit();
  });
});
