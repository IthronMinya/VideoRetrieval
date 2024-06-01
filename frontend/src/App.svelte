<script>
  // @ts-nocheck

  import { selected_images, scroll_height, in_video_view, lion_text_query } from "./stores.js";
  import ImageList from "./ImageList.svelte";

  import VirtualList from "./VirtualListNew.svelte";

  import Button from "@smui/button";

  import Select, { Option } from "@smui/select";

  import Fab, { Icon } from "@smui/fab";

  import { onMount } from "svelte";

  import { generate } from "random-words";

  let evaluation_name = "";
  let task_id = "";
  let user_id;
  let timer;

  let task_ids_collection = [];

  let start;
  let end;
  let image_items = [];

  let custom_result = "";

  let textContainsGreaterThan = false;

  let max_display_size = 1000;

  let max_labels = 10;
  let chart_labels = 10;

  let row_size = 4;
  let prepared_display = null;
  $: {
    evaluation_ids;
    task_ids;
    set_scroll($scroll_height);
    prepared_display;
    filtered_lables;
    textContainsGreaterThan = $lion_text_query.includes(">");
  }

  let datasets = ["V3C", "MVK", "VBSLHE", "LSC"];

  let users = ["lscteam211", "lscteam212", "lscteam213", "PraK1", "PraK5"];

  let passwords = ["93YHg88hAfbJNV2", "93YHg88hAfbJNV2", "93YHg88hAfbJNV2", "G5L>q:e{", "gb~.8mMy"];

  let value_dataset = "LSC";

  let username = "lscteam211";

  const dres_server = "https://vbs.videobrowsing.org";
  const service_server = "http://vbs-backend-data-layer-1:80"; //"http://acheron.ms.mff.cuni.cz:42032";

  let send_results = "";

  let dragged_url = null;

  let action_pointer = -1;

  let file = null;

  let filtered_lables = [];

  let file_labels = [];

  let labelColorMap = {};

  let virtual_list;

  let unique_video_frames = false;
  let image_video_on_line = false;
  let image_hour_on_line = false;

  let is_correct = false;

  let filters = [];

  let evaluation_ids = [];
  let evaluation_names = [];
  let task_ids = [];
  let session_id;

  let logging = true;

  initialization();

  get_session_id_for_user();

  function set_dataset() {
    initialization();
  }

  function set_task_id() {
    let t = task_ids_collection[evaluation_names.indexOf(evaluation_name)];

    for (let i = 0; i < t.length; i++) {
      task_ids.push(t[i].name);
    }

    task_ids = task_ids;
  }

  function getKeyByValue(obj, value) {
    return Object.keys(obj).filter(
      (key) => obj[key]["id"] && obj[key]["id"][0] === value[0] && obj[key]["id"][1] === value[1]
    );
  }

  async function handle_submission(results, text = "") {
    is_correct = false;

    // if evaluation_name is undefined, we cannot submit anything
    if (evaluation_name === undefined || evaluation_name === "") {
      console.log("No evaluation name selected.");
      return;
    }
    
    let image_data = image_items;
    let eval_id = evaluation_ids[evaluation_names.indexOf(evaluation_name)];

    let request_url = dres_server + "/api/v2/submit/" + eval_id + "?session=" + session_id;

    let answers = [];

    if (results == null) {
      let answer = {
        text: text, //text - in case the task is not targeting a particular content object but plaintext
        mediaItemName: null, // item -  item which is to be submitted
        mediaItemCollectionName: null, // collection - does not usually need to be set
        start: null, //start time in milliseconds
        end: null, //end time in milliseconds, in case an explicit time interval is to be specified
      };

      answer = { answers: [answer], taskId: task_id };

      answers.push(answer);
    } else {
      for (let i = 0; i < results.length; i++) {
        let answer = {
          'text': null, //text - in case the task is not targeting a particular content object but plaintext
          'mediaItemName': results[i][0], // item -  item which is to be submitted
          'mediaItemCollectionName': null, // collection - does not usually need to be set
          'start': null, //start time in milliseconds
          'end': null //end time in milliseconds, in case an explicit time interval is to be specified
        };

        if (value_dataset !== 'LSC') {
          let result_key = getKeyByValue(image_data, results[i]);

          let interval = image_data[result_key].time;

          answer.start = Math.round(interval[2]); 
          answer.end = Math.round(interval[3]);
        } else {
          answer.mediaItemName = results[i][0] + "_" + results[i][1];
        }

        answer = { answers: [answer], taskId: task_id };

        answers.push(answer);
      }
    }

    let request_body = JSON.stringify({
      answerSets: answers,
    });

    console.log(request_body);

    let response = await fetch(request_url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: request_body,
    });

    if (response.ok) {
      let res = await response.json();

      console.log(res);

      is_correct = res["correct"] == "true"; //TODO: check if this is correct

      if (logging) {
        let request_body = {
          log : {
            answers: answers,
            action: "submit"
          },
          username: username,
        };

        request_body = JSON.stringify(request_body);

        const response2 = await fetch(`${window.location.origin}/append_user_log`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: request_body,
          }
        );

        if (response2.ok) {
          console.log(await response2.text());
        }
      }
    }
  }

  async function get_session_id_for_user() {
    evaluation_ids = [];
    evaluation_names = [];
    task_ids_collection = [];
    task_ids = [];

    evaluation_name = "";
    task_id = "";

    let request_url = dres_server + "/api/v2/login";

    let request_body = JSON.stringify({
      username: username,
      password: passwords[users.indexOf(username)],
    });

    let response = await fetch(request_url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: request_body,
    });

    if (response.ok) {
      let res = await response.json();
      user_id = res["id"];
      session_id = res["sessionId"];

      console.log(user_id, session_id);
    } else {
      console.log(response);
    }

    let evaluations_url = dres_server + "/api/v2/client/evaluation/list?session=" + session_id;

    let evaluations_req = await fetch(evaluations_url, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (evaluations_req.ok) {
      let res = await evaluations_req.json();

      console.log(res);

      for (let i = 0; i < res.length; i++) {
        evaluation_ids.push(res[i].id);
        evaluation_names.push(res[i].name);
        task_ids_collection.push(res[i].taskTemplates);
      }

      console.log(evaluation_ids);
      console.log(evaluation_names);

      evaluation_ids = evaluation_ids;
      evaluation_names = evaluation_names;
    }

    if (logging) {
      let url_log = `${window.location.origin}/create_user_log`;
      let body = JSON.stringify({
        username: username,
      });
      const response_create_log = await fetch(url_log, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: body,
        });
      
        if (response_create_log.ok) {
        console.log(await response_create_log.text());
      }
    }
  }

  function set_scroll(scroll) {
    if (image_items != null) {
      image_items["scroll"] = scroll;
    }
  }

  function scrollToHeight(height) {
    setTimeout(() => {
      if (virtual_list) {
        virtual_list.scrollToScrollHeight(height, { behavior: "auto" });
        virtual_list.handle_scroll();
      }
    }, 50);
  }

  function scroll_to_index(index) {
    setTimeout(() => {
      if (virtual_list) {
        virtual_list.scrollToIndex(index, { behavior: "auto" });
        virtual_list.handle_scroll();
      }
    }, 50);
  }

  function updateButtonState(buttonId, condition) {
    const button = document.getElementById(buttonId);
    button.style.backgroundColor = condition ? "lightgrey" : "grey";
    button.style.cursor = condition ? "default" : "pointer";
  }

  async function reloading_display(video_image_id = 0) {
    is_correct = false;

    start = 0;
    updateButtonState("previous", action_pointer <= 0);
    updateButtonState("next", 9 <= action_pointer);

    let scroll_index;

    if (image_items != null) {
      $in_video_view = image_items["method"] === "show_video_frames";
      $lion_text_query = image_items["method"] === "textquery" ? image_items["query"] : "";

      console.log("reloading display");

      let rows = [];
      let row = -1;
      let row_ids = {};
      let s = 0;

      let temp_selection = [];
      const currentMethod = image_items["method"];

      for (let i = 0; i < image_items.length; i++) {
        const currentItem = image_items[i];
        const currentItemId = currentItem["id"];

        if (currentMethod == "show_video_frames" && video_image_id != 0 && currentItemId[0] == video_image_id[0] && currentItemId[1] == video_image_id[1]) {
          scroll_index = rows.length - 1;
        }

        if (currentItemId in $selected_images) {
          temp_selection.push(currentItemId);
        }

        if (!currentItem.hasOwnProperty("disabled") || !currentItem["disabled"]) {
          if (currentMethod != "show_video_frames" && unique_video_frames) {
            if (!row_ids.hasOwnProperty(currentItemId[0])) {
              row_ids[currentItemId[0]] = row;
              if (s % row_size == 0) {
                rows[++row] = [];
              }
              rows[row].push(currentItem);
              s += 1;
            }
          } else if (currentMethod != "show_video_frames" && image_video_on_line) {
            if (row_ids.hasOwnProperty(currentItemId[0])) {
              rows[row_ids[currentItemId[0]]].push(currentItem);
            } else {
              row_ids[currentItemId[0]] = ++row;
              rows[row] = [currentItem];
            }
          } else if (image_hour_on_line) {
            let hour = currentItemId[0] + currentItemId[1].slice(0, 2);
            console.log(hour);
            if (row_ids.hasOwnProperty(hour)) {
              rows[row_ids[hour]].push(currentItem);
            } else {
              row_ids[hour] = ++row;
              rows[row] = [currentItem];
            }
          } else {
            if (s % row_size == 0) {
              rows[++row] = [];
            }
            rows[row].push(currentItem);
            s += 1;
          }
        }
      }

      $selected_images = temp_selection;

      prepared_display = rows;

      if (image_items["method"] == "show_video_frames" && video_image_id != 0 &&  scroll_index != undefined) {
        scroll_to_index(scroll_index > 0 ? scroll_index : 0);
      }

      create_chart();

    } else {
      prepared_display = null;
    }
  }

  onMount(() => {
    window.addEventListener("resize", reloading_display);
    return () => {
      window.removeEventListener("resize", reloading_display);
    };
  });

  function noopHandler(evt) {
    evt.preventDefault();
  }

  function drop(evt) {
    evt.preventDefault();
    file = evt.dataTransfer.files[0];

    if (file && file.type.startsWith("image/")) {
      const reader = new FileReader();

      reader.onload = () => {
        dragged_url = reader.result;
      };

      reader.readAsDataURL(file);

      get_scores_by_image_upload();
    }
  }

  async function send_results_custom() {
    if (timer) {
      timer.stop();
    }

    send_results = custom_result;
    $selected_images = [];

    await handle_submission(null, send_results);
  }

  async function send_results_single(event) {
    if (timer) {
      timer.stop();
    }

    send_results = event.detail.image_id;
    $selected_images = [];

    await handle_submission([send_results]);
  }

  async function send_results_multiple() {
    if (timer) {
      timer.stop();
    }

    send_results = " ";

    $selected_images.forEach((selection) => {
      send_results += `${selection}; `;
    });

    await handle_submission($selected_images);

    send_results = send_results.slice(0, -2); // remove last space and semicolon

    $selected_images = [];
  }

  async function video_images(event) {
    const request_url = service_server + "/getVideoFrames/";

    let selected_item = event.detail.image_id;

    let request_body = {
      item_id: String(selected_item[0]) + "_" + String(selected_item[1]),
      k: -1,
      dataset: value_dataset,
      add_features: 1,
      speed_up: 1,
      max_labels: max_labels,
    };

    if (value_dataset == 'LSC') {
      request_body.k = 500;
    }

    request_body = JSON.stringify(request_body);

    request_handler(request_url, request_body, false, "show_video_frames", false, [selected_item[0], selected_item[1]], selected_item, true);
  }

  async function initialization() {
    // Read labels from the text file
    file_labels = await readTextFile("./assets/" + value_dataset + "-nounlist.txt");

    console.log("./assets/" + value_dataset + "-nounlist.txt");

    let url = `${window.location.origin}/get_filters`;
    let response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        dataset: value_dataset,
      }),
    });

    if (response.ok) {
      let res = await response.json();
      for (let i = 0; i < res.length; i++) {
        filters.push({ name: res[i], value: '' });
      }
    }

    // setting this to null temporarily will make a loading display to appear
    prepared_display = null;

    let q = generate();

    const request_url = service_server + "/textQuery/";

    const request_body = JSON.stringify({
      query: q,
      k: max_display_size,
      dataset: value_dataset,
      add_features: 1,
      speed_up: 1,
      max_labels: max_labels,
    });

    request_handler(request_url, request_body, true, "", false, "", 0, false, true);
  }

  function handleKeypress(event) {
    var key = event.keyCode || event.which;
    if (key == 13) {
      event.preventDefault();
      get_scores_by_text();
    }
    textContainsGreaterThan = $lion_text_query.includes(">");
  }

  async function request_handler(request_url, request_body, init = false, method = "", image_upload = false, query = "", video_image_id = 0, is_sorted = false, reset = false) {
    // setting this to null temporarily will make a loading display to appear
    prepared_display = null;

    filtered_lables = [];

    let response;

    try {
      const url = `${window.location.origin}/send_request_to_service`;
      request_body = {
        url: request_url,
        body: request_body,
        image_upload: image_upload,
        init: init,
        sorted: is_sorted,
        dataset: value_dataset,
        username: username,
        reset: reset,
      };

      if (value_dataset == 'LSC') {
        let bodyObject = JSON.parse(request_body.body);
        bodyObject.model = 'clip-vit-webli';
        request_body.body = JSON.stringify(bodyObject);
      }

      request_body = JSON.stringify(request_body);

      if (!image_upload) {
        response = await fetch(url, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: request_body,
        });
      } else {
        response = await fetch(url, {
          method: "POST",
          body: request_body,
        });
      }

      if (!response.ok) {
        throw new Error("Request failed");
      }

      let responseData = await response.json();
      responseData = responseData[0];
      action_pointer = responseData[1];

      console.log(responseData);

      responseData.forEach(item => {
        item.disabled = filtered_lables.length > 0 ? !filtered_lables.some(lab => item.label.includes(lab)) : false;
      });

      image_items = responseData;

      if (method != "") {
        image_items["method"] = method;
      }
      if (query != "") {
        image_items["query"] = query;
      }

      // reset the selection
      $selected_images = [];

      if (video_image_id != 0) {
        reloading_display(video_image_id);
      } else {
        reloading_display();
      }
    } catch (error) {
      console.error(error);
    }
  }

  async function get_scores_by_text() {
    const request_url = service_server + (textContainsGreaterThan ? "/temporalQuery/" : "/textQuery/");

    const request_body = JSON.stringify({
      query: $lion_text_query,
      k: max_display_size,
      dataset: value_dataset,
      add_features: 1,
      speed_up: 1,
      max_labels: max_labels,
    });

    await request_handler(request_url, request_body, false, textContainsGreaterThan ? "temporalquery" : "textquery", false, $lion_text_query);
  }

  async function get_scores_by_image(event) {
    const request_url = service_server + "/imageQueryByID/";

    let selected_item = event.detail.image_id;

    const request_body = JSON.stringify({
      video_id: selected_item[0],
      frame_id: selected_item[1],
      k: max_display_size,
      dataset: value_dataset,
      add_features: 1,
      speed_up: 1,
      max_labels: max_labels,
    });

    await request_handler(request_url, request_body, false, "image_query", false, [selected_item[0], selected_item[1]]);
  }

  async function get_scores_by_image_upload() {
    if (file === null) {
      return null;
    }

    const request_url = service_server + "/imageQuery/";

    const params = {
      k: max_display_size,
      add_features: 1,
      dataset: value_dataset,
      speed_up: 1,
      max_labels: max_labels,
    };

    const request_body = new FormData();
    request_body.append("image", file);
    request_body.append("query_params", JSON.stringify(params));

    await request_handler(request_url, request_body, false, "image_upload_query", true);
  }

  async function bayesUpdate() {
    if ($selected_images.length == 0) {
      console.log(
        "Nothing was selected. Cannot perform the Bayes update without a positve example.",
      );
      return null;
    }

    const url = `${window.location.origin}/bayes`;

    let response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        selected_images: $selected_images,
        username: username,
      }),
    });

    let responseData = await response.json();

    image_items = responseData;

    // reset the selection
    $selected_images = [];

    reloading_display();
    scrollToHeight(0);
  }

  async function traverse_states(direction) {
    // no action when we are at the initialization or there is no next action yet.
    if ( (direction == -1 && action_pointer <= 0) || (direction == 1 && action_pointer >= 9) ) {
      return null;
    }

    let url = `${window.location.origin}/${direction === -1 ? 'back' : 'forward'}`;

    let response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        username: username,
      }),
    });

    let responseData = await response.json();

    if (responseData.length != 2) {
      return null;
    }

    image_items = responseData[0];
    action_pointer = responseData[1];

    reloading_display();

    // will be previous if action is -1 and next if action is + 1
    scrollToHeight(0);
  }

  async function readTextFile(filePath) {
    try {
      const response = await fetch(filePath);
      const data = await response.text();
      return data.split("\n").map((label) => label.trim());
    } catch (error) {
      console.error("Error reading text file:", error);
      return [];
    }
  }

  async function findTopNNumbersWithLabels(dictionary, n) {
    const allNumbers = Object.values(dictionary).flatMap((obj) => obj.label);
    const numberOccurrences = {};

    // Count occurrences and associate with labels
    allNumbers.forEach((number) => {
      const label = file_labels[number];
      numberOccurrences[label] = (numberOccurrences[label] || 0) + 1;
    });

    // Sort the array based on occurrences and then label
    const sortedLabels = Object.keys(numberOccurrences).sort((a, b) => {
      const frequencyComparison = numberOccurrences[b] - numberOccurrences[a];
      if (frequencyComparison !== 0) {
        return frequencyComparison;
      }
      return a.localeCompare(b);
    });

    // Take the top N labels with occurrences
    const topNLabels = sortedLabels.slice(0, n).map((label) => ({
      label,
      occurrences: numberOccurrences[label],
      id: file_labels.indexOf(label),
    }));

    return topNLabels;
  }

  async function label_click(event) {
    const clickedId = event;
    const clickedLabel = file_labels[clickedId];

    console.log(`Clicked bar with label: ${clickedLabel}, Id: ${clickedId}`);

    if (filtered_lables.includes(clickedId)) {
      // restore disabled items again
      filtered_lables.splice(filtered_lables.indexOf(clickedId), 1);

      let temp_items = window.structuredClone(image_items); // deepcopy

      if (filtered_lables.length > 0) {
        for (const [key, value] of Object.entries(temp_items)) {
          if (key == "scroll" || key == "method" || key == "query") {
            continue;
          }
          temp_items[key]["disabled"] = true;
        }

        let one_not_included = false;
        for (const [key, value] of Object.entries(temp_items)) {
          if (key == "scroll" || key == "method" || key == "query") {
            continue;
          }
          one_not_included = false;

          for (let i = 0; i < filtered_lables.length; i++) {
            if (!temp_items[key].label.includes(filtered_lables[i])) {
              one_not_included = true;
            }
          }
          if (!one_not_included) {
            temp_items[key]["disabled"] = false;
          }
        }
      } else {
        for (const [key, value] of Object.entries(temp_items)) {
          if (key == "scroll" || key == "method" || key == "query") {
            continue;
          }
          temp_items[key]["disabled"] = false;
        }
      }

      let new_rank = 0;
      for (const [key, value] of Object.entries(temp_items)) {
        if (key == "scroll" || key == "method" || key == "query") {
          continue;
        }
        if (temp_items[key]["disabled"] == false) {
          temp_items[key].rank = new_rank;
          new_rank++;
        }
      }

      image_items = temp_items;

    } else {
      filtered_lables.push(clickedId);

      // Filter out elements in the image_items dictionary that don't contain the clicked label
      let temp_items = window.structuredClone(image_items); // deepcopy

      for (const [key, value] of Object.entries(temp_items)) {
        if (key == "scroll" || key == "method" || key == "query") {
          continue;
        }
        temp_items[key]["disabled"] = false;
      }

      for (const [key, value] of Object.entries(temp_items)) {
        if (key == "scroll" || key == "method" || key == "query") {
          continue;
        }
        for (let i = 0; i < filtered_lables.length; i++) {
          if (!temp_items[key].label.includes(filtered_lables[i])) {
            temp_items[key]["disabled"] = true;
          }
        }
      }

      let new_rank = 0;
      for (const [key, value] of Object.entries(temp_items)) {
        if (key == "scroll" || key == "method" || key == "query") {
          continue;
        }
        if (temp_items[key]["disabled"] == false) {
          temp_items[key].rank = new_rank;
          new_rank++;
        }
      }

      image_items = temp_items;
    }

    // trigger reload of labels under chart
    filtered_lables = filtered_lables;

    reloading_display();
  }

  function generateColor(label) {
    // Check if the label already has a color assigned
    if (!labelColorMap[label]) {
      // Generate a random color for the label
      var r = Math.floor(Math.random() * 256);
      var g = Math.floor(Math.random() * 256);
      var b = Math.floor(Math.random() * 256);

      // Mix with white to create a pastel effect
      var mixColor = 255; // White color
      r = Math.floor((r + mixColor) / 2);
      g = Math.floor((g + mixColor) / 2);
      b = Math.floor((b + mixColor) / 2);

      labelColorMap[label] = "rgba(" + r + "," + g + "," + b + ", 1.0)";
    }

    return labelColorMap[label];
  }

  async function create_chart() {
    if ( image_items[0] == null || image_items[0]["label"] == null ) {
      return;
    }

    let temp_items = image_items.filter(
      (item) => !(item.hasOwnProperty("disabled") && item["disabled"]),
    );

    const topNumbersWithOccurrences = await findTopNNumbersWithLabels(
      temp_items,
      chart_labels,
    );

    let allLabels = Object.values(topNumbersWithOccurrences).flatMap(
      (obj) => obj.label
    );
    let allOccurrences = Object.values(topNumbersWithOccurrences).flatMap(
      (obj) => obj.occurrences
    );
    let allIds = Object.values(topNumbersWithOccurrences).flatMap(
      (obj) => obj.id
    );

    let border_colors = allIds.map((id) => filtered_lables.includes(id) ? "#FF0000" : "rgba(0, 0, 0, 0.0)");

    const canvas = document.getElementById("myChart");

    // clear previous canvas
    let new_canvas = document.createElement("canvas");
    new_canvas.setAttribute("id", "myChart");
    new_canvas.setAttribute("class", "menu_item");
    new_canvas.setAttribute("style", "margin-left: 2em; margin-right: 2em;  height: 17em");
    canvas.replaceWith(new_canvas);

    const ctx = document.getElementById("myChart").getContext("2d"); // 2d context

    let myHorizontalBarChart = new Chart(ctx, {
      type: "bar",
      data: {
        labels: allLabels,
        datasets: [
          {
            label: "Display Clusters",
            borderColor: border_colors,
            borderWidth: 2,
            data: allOccurrences,
          },
        ],
      },
      options: {
        onClick: async function (event, elements) {
          if (elements && elements.length > 0) {
            // Get the index of the clicked bar
            const clickedIndex = elements[0].index;

            const clickedLabel = allLabels[clickedIndex];
            const clickedId = allIds[clickedIndex];

            console.log(
              `Clicked bar with label: ${clickedLabel}, Id: ${clickedId}`
            );

            if (filtered_lables.includes(clickedId)) {
              // restore disabled items again
              filtered_lables.splice(filtered_lables.indexOf(clickedId), 1);
              filtered_lables = filtered_lables;

              let temp_items = window.structuredClone(image_items); // deepcopy

              if (filtered_lables.length > 0) {
                for (const [key, value] of Object.entries(temp_items)) {
                  if (key == "scroll" || key == "method" || key == "query") {
                    continue;
                  }
                  temp_items[key]["disabled"] = true;
                }

                let one_not_included = false;

                for (const [key, value] of Object.entries(temp_items)) {
                  if (key == "scroll" || key == "method" || key == "query") {
                    continue;
                  }
                  one_not_included = false;

                  for (let i = 0; i < filtered_lables.length; i++) {
                    if (!temp_items[key].label.includes(filtered_lables[i])) {
                      one_not_included = true;
                    }
                  }
                  if (!one_not_included) {
                    temp_items[key]["disabled"] = false;
                  }
                }
              } else {
                for (const [key, value] of Object.entries(temp_items)) {
                  if (key == "scroll" || key == "method" || key == "query") {
                    continue;
                  }
                  temp_items[key]["disabled"] = false;
                }
              }

              let new_rank = 0;
              for (const [key, value] of Object.entries(temp_items)) {
                if (key == "scroll" || key == "method" || key == "query") {
                  continue;
                }
                if (temp_items[key]["disabled"] == false) {
                  temp_items[key].rank = new_rank;
                  new_rank++;
                }
              }

              image_items = temp_items;
            } else {
              filtered_lables.push(clickedId);
              filtered_lables = filtered_lables;

              // Filter out elements in the image_items dictionary that don't contain the clicked label
              let temp_items = window.structuredClone(image_items); // deepcopy

              for (const [key, value] of Object.entries(temp_items)) {
                if (key == "scroll" || key == "method" || key == "query") {
                  continue;
                }
                temp_items[key]["disabled"] = false;
              }

              for (const [key, value] of Object.entries(temp_items)) {
                if (key == "scroll" || key == "method" || key == "query") {
                  continue;
                }
                for (let i = 0; i < filtered_lables.length; i++) {
                  if (!temp_items[key].label.includes(filtered_lables[i])) {
                    temp_items[key]["disabled"] = true;
                  }
                }
              }

              let new_rank = 0;
              for (const [key, value] of Object.entries(temp_items)) {
                if (key == "scroll" || key == "method" || key == "query") {
                  continue;
                }
                if (temp_items[key]["disabled"] == false) {
                  temp_items[key].rank = new_rank;
                  new_rank++;
                }
              }

              image_items = temp_items;
            }

            reloading_display();
          }
        },
        indexAxis: "y",
        scales: {
          x: {
            beginAtZero: true,
          },
          y: {
            position: "left",
            reverse: false,
            callback: function (value) {
              if (value % 1 === 0) {
                return value;
              }
            },
          },
        },
        plugins: {
          legend: {
            display: false,
          },
          tooltip: {
            callbacks: {
              label: function (context) {
                return context.dataset.data[context.dataIndex];
              },
            },
          },
        },
      },
    });

    // Dynamically assign colors based on labels
    myHorizontalBarChart.data.datasets[0].backgroundColor = myHorizontalBarChart.data.labels.map(generateColor);
    myHorizontalBarChart.update(); // Update the chart
  }

  async function applyFilters() {
    let url = service_server + "/filter/";

    let filters_to_apply = filters.filter((filter) => filter.value !== "");
    filters_to_apply = filters_to_apply.reduce((acc, filter) => {
      acc[filter.name] = filter.value;
      return acc;
    }, {});
    
    const request_body = JSON.stringify({
      filters: filters_to_apply,
      username: username,
      k: max_display_size,
      dataset: value_dataset,
      add_features: 1,
      speed_up: 1,
      max_labels: max_labels,
    });

    request_handler(url, request_body, false, "", false, "", 0, false, true);
  }
</script>

<main>
  <div class="viewbox">
    <div class="top-menu">
      <div class="top-menu-item top-negative-offset">
        <Select
          on:SMUISelect:change={get_session_id_for_user}
          bind:value={username}
          label="Select User"
        >
          {#each users as user}
            <Option value={user}>{user}</Option>
          {/each}
        </Select>
      </div>
      <div class="top-menu-item top-negative-offset">
        <Select
          on:SMUISelect:change={set_task_id}
          bind:value={evaluation_name}
          label="Evaluation ID"
        >
          {#each evaluation_names as e}
            <Option value={e}>{e}</Option>
          {/each}
        </Select>
      </div>
      <div class="top-menu-item top-negative-offset">
        <Select
          on:SMUISelect:change={task_id}
          bind:value={task_id}
          label="Task ID"
        >
          {#each task_ids as t}
            <Option value={t}>{t}</Option>
          {/each}
        </Select>
      </div>
      <div class="top-menu-item top-negative-offset">
        <Select
          on:SMUISelect:change={set_dataset}
          bind:value={value_dataset}
          label="Select Dataset"
        >
          {#each datasets as dataset}
            <Option value={dataset}>{dataset}</Option>
          {/each}
        </Select>
      </div>
      <div class="top-menu-item top-negative-offset3">
        <Button
          color="primary"
          on:click={send_results_multiple}
          variant="raised"
        >
          <span class="resize-text">Send Selected Images</span>
        </Button>
      </div>
      <div class="top-input">
        <input
          class="top-menu-item resize-text top-offset"
          bind:value={custom_result}
          placeholder="Your custom result message"
        />
      </div>
      <div class="top-menu-item top-negative-offset3">
        <Button color="primary" on:click={send_results_custom} variant="raised">
          <span class="resize-text">Send custom text</span>
        </Button>
      </div>
      {#if is_correct}
        <span style="color: green;">&#43;</span>
      {/if}
    </div>

    <div class="horizontal">
      <div class="menu">
        <br />
        <div class="buttons">
          <div class="centering" style="margin-bottom:0.5em;">
            <Fab
              id="previous"
              on:click={() => traverse_states(-1)}
              extended
              ripple={false}
            >
              <Icon style="font-size:20px;" class="material-icons"
                >arrow_back</Icon
              >
            </Fab>
            <Fab
              id="next"
              on:click={() => traverse_states(1)}
              extended
              ripple={false}
            >
              <Icon style="font-size:20px;" class="material-icons"
                >arrow_forward</Icon
              >
            </Fab>
          </div>
          <!--{#if send_results.length > 0}
              <span>Your send results: {send_results}</span>
            {/if}
            <div class="timer centering" style="margin-bottom:0.5em;">
              <Timer bind:this={timer}/>
            </div>-->
          <textarea
            id="text_query_input"
            class="menu_item resize-text"
            class:blue-text={textContainsGreaterThan}
            bind:value={$lion_text_query}
            placeholder="Your text query"
            on:keypress={handleKeypress}
            style="height: 80px;"
          />
          <Button
            class="menu_item menu_button"
            color="secondary"
            on:click={get_scores_by_text}
            variant="raised"
          >
            <span class="resize-text">Submit Text Query</span>
          </Button>
          <div class="filedrop-container menu_item">
            <!-- svelte-ignore a11y-no-static-element-interactions -->
            <div
              class="file-drop-area menu_item"
              on:dragenter={noopHandler}
              on:dragexit={noopHandler}
              on:dragover={noopHandler}
              on:drop={drop}
            >
              <span class="fake-btn">Choose files</span>
              <span class="file-msg">or drag and drop file here</span>
              <input class="file-input" type="file" />
            </div>
            {#if dragged_url != null}
              <div class="image-preview-container menu_item">
                <img
                  class="preview_image"
                  alt="preview upload"
                  src={dragged_url}
                />
              </div>
            {/if}
          </div>
          <Button
            class="menu_item menu_button"
            color="secondary"
            on:click={bayesUpdate}
            variant="raised"
          >
            <span class="resize-text">Bayes Update</span>
          </Button>

          {#each filters as filter (filter.name)}
            <label>
              {filter.name}
              <input type="text" bind:value={filter.value} placeholder="Enter {filter.name} ..." />
            </label>
          {/each}
          <button on:click={applyFilters}>Apply Filters</button>

          <canvas class="menu_item" id="myChart"></canvas>
          <div id="customLegend" class="menu_item"></div>
          {#key filtered_lables}
            {#if filtered_lables.length > 0}
              <p>Active label filter</p>
            {/if}
            {#each filtered_lables as label}
              <!-- svelte-ignore a11y-click-events-have-key-events -->
              <!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
              <p class="active_label" on:click={() => label_click(label)}>
                {file_labels[label]}
              </p>
            {/each}
          {/key}
          <br />
          <div>
            <label for="unique_video_frames">Limit Frames per Video to 1</label>
            <input
              type="checkbox"
              id="unique_video_frames"
              name="unique_video_frames"
              bind:checked={unique_video_frames}
              on:change={reloading_display}
            />
          </div>
          <br />
          <div>
            <label for="image_video_on_line">
              {#if value_dataset === 'LSC'}
                Images from same day on one line
              {:else}
                Images from video on one line
              {/if}
            </label>
            <input
              type="checkbox"
              id="image_video_on_line"
              name="image_video_on_line"
              bind:checked={image_video_on_line}
              on:change={reloading_display}
            />
          </div>
          <br />
          {#if value_dataset === 'LSC'}
            <label for="image_hour_on_line">
              Images from same hour on one line
            </label>
            <input 
              type="checkbox" 
              id="image_hour_on_line" 
              name="image_hour_on_line" 
              bind:checked={image_hour_on_line} 
              on:change={reloading_display}>
          {/if}
          <div>
            <label for="labels_per_frame">Labels per Frame</label>
            <input
              type="number"
              id="labels_per_frame"
              name="labels_per_frame"
              min="1"
              max="10"
              bind:value={max_labels}
            />
          </div>
          <br />
          {#if prepared_display !== null}
            <p>
              Total Images: {prepared_display.reduce(
                (count, current) => count + current.length,
                0,
              )}
            </p>
          {/if}
        </div>
      </div>
      <div id="container">
        {#if prepared_display === null}
          <p>...loading</p>
        {:else}
          <VirtualList
            items={prepared_display}
            bind:this={virtual_list}
            bind:start
            bind:end
            let:item
          >
            <ImageList
              on:send_result={send_results_single}
              on:similarimage={get_scores_by_image}
              on:video_images={video_images}
              row={item}
              bind:row_size
              labels={file_labels}
            />
          </VirtualList>
        {/if}
      </div>
    </div>
  </div>
</main>

<style>
  .active_label {
    color: red;
    text-align: left;
    margin-left: 2em;
    margin-right: 2em;
    padding: 0.5em;
    background-color: lightgray;
    cursor: pointer;
  }

  #myChart {
    width: 80%;
    float: left;
    margin-left: 2em;
  }

  .centering {
    display: flex;
    flex-direction: row;
    justify-content: center;
    width: 100%;
  }

  .horizontal {
    display: flex;
    flex: 1;
  }

  .resize-text {
    font-size: 0.75em;
  }

  .file-drop-area {
    position: relative;
    display: flex;
    align-items: center;
    height: 2em;
    margin-left: 1em;
    margin-right: 1em;
    border: 1px dashed rgba(61, 61, 61, 0.4);
    border-radius: 3px;
    transition: 0.2s;
    &.is-active {
      background-color: rgba(255, 255, 255, 0.05);
    }
  }

  .top-menu {
    flex: 1;
    display: flex;
  }

  .top-menu-item {
    display: flex;
    margin-left: 1em;
    margin-bottom: 0.25em;
  }

  .top-offset {
    margin-top: 1.25em;
  }

  .top-input {
    height: 100%;
    margin-top: -0.6em;
  }

  .fake-btn {
    flex-shrink: 0;
    background-color: rgba(54, 53, 53, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 0.1em;
    padding: 0.2em 0.4em;
    margin-right: 0.25em;
    font-size: 0.75em;
    text-transform: uppercase;
    text-overflow: ellipsis;
    white-space: nowrap;
    overflow: hidden;
  }

  .file-msg {
    font-size: 0.75em;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .file-input {
    position: absolute;
    left: 0;
    top: 0;
    height: 100%;
    width: 100%;
    cursor: pointer;
    opacity: 0;
    &:focus {
      outline: none;
    }
  }

  #text_query_input {
    height: 10em;
    margin-top: 2em;
  }

  #container {
    min-height: 200px;
    height: calc(100vh - 3em);
    width: 85%;
    float: left;
    background-color: rgb(255, 255, 255);
  }

  .filedrop-container {
    display: block;
    margin-left: auto;
    margin-right: auto;
    width: 90%;
  }

  .image-preview-container {
    width: 100%;
    height: 6em;
    display: block;
  }

  .preview_image {
    height: 100%;
    width: 100%;
    object-fit: contain;
  }

  .top-negative-offset {
    margin-top: -1.5em;
  }

  .top-negative-offset3 {
    margin-top: -0.2em;
  }

  .menu {
    height: calc(100vh - 3em);
    overflow-y: auto;
    scrollbar-width: none; /* For Firefox */
    -ms-overflow-style: none; /* For Internet Explorer and Edge */
  }

  .menu::-webkit-scrollbar {
    /* For Chrome, Safari and Opera */
    display: none;
  }

  .blue-text {
    color: blue;
  }
</style>
