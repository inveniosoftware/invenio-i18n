/*
 * SPDX-FileCopyrightText: 2016-2018 CERN.
 * SPDX-FileCopyrightText: 2016 TIND.
 * SPDX-License-Identifier: MIT
 */

import * as $ from "jquery/dist/jquery";

$(document).ready(function() {
  $("#lang-code").on("change", function() {
    $("#language-code-form").submit();
  });
});
