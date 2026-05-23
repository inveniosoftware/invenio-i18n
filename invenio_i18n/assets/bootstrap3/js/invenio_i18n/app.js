/*
 * SPDX-FileCopyrightText: 2016-2018 CERN.
 * SPDX-FileCopyrightText: 2016 TIND.
 * SPDX-License-Identifier: MIT
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
