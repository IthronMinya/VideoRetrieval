
<script>
    import { logEvent } from './Logger.js';
    import { selected_images, in_video_view } from './stores.js';
    import { fade } from 'svelte/transition';
    import { lion_text_query } from './stores.js';
    import VideoPlayer from 'svelte-video-player';
    import Button from "@smui/button";
    import { createEventDispatcher, onMount, onDestroy } from 'svelte';
    const dispatch = createEventDispatcher()

    export let img;
    export let row_size;
    export let labels;

    export let selected;
    let hover = false;
    let video = false;
    let large = false;

    let container;
    let observer;
    let video_time;

    function showVideo(){
        video = true;
        logEvent("videoBrowse", img.id);
    }

    function largeImage(){
        large = true;
        logEvent("detail", img.id);
    }

    function similarimage(){
        dispatch('similarimage');
    }

    function video_images(){
        dispatch('video_images');
    }

    function send_result(){
        dispatch('send_result');
    }

    function add_label_to_query(label) {
        $lion_text_query += ($lion_text_query == '' ? '' : ', ') + label;
        logEvent("usedLabel", label);
    }

    export function imgClick() {

        if (!selected){
            $selected_images = [...$selected_images, img.id];

        }else{
            $selected_images=$selected_images.filter(e => e !== img.id);
        }

        selected = !selected;

        console.log($selected_images);
    }

    function send_result_videoframe(){
	const videoElement = container.querySelector('video'); 
	if (videoElement) {
	    video_time = videoElement.currentTime;
	}
	dispatch('send_result_videoframe', {video_time});
    }

    onMount(() => {
      // Create a MutationObserver to monitor the container for changes
      observer = new MutationObserver(() => {
        // Look for the <video> element anywhere inside the container (including children)
        const videoElement = container.querySelector('video'); 
        if (videoElement) {
          // Stop observing once the video is found
          observer.disconnect();
          // Ensure metadata is loaded before setting currentTime
          videoElement.addEventListener(
            'loadedmetadata',
            () => {
              videoElement.currentTime = Math.round(img.time[1] / 1000);
              videoElement.play();
            }
          );
          videoElement.addEventListener("loadeddata", () => {
            console.log("video loaded");
            logEvent("videoDataLoaded");
            });
          videoElement.addEventListener("played", () => {
            console.log("handle play");
            let currentTime = videoElement.currentTime.toFixed(2);

            logEvent("videoStartPlay", String(currentTime));
            });

          videoElement.addEventListener("seeked", () => {
            let currentTime = videoElement.currentTime.toFixed(2);
            logEvent("videoSkippedTo", String(currentTime));
            console.log(String(currentTime));
            });
        }
      });

      // Observe the container for changes, including children
      observer.observe(container, { childList: true, subtree: true });
    });


    onDestroy(() => {
      // Clean up the observer when the component is destroyed
      if (observer) {
        observer.disconnect();
      }
    });


</script>

<!-- svelte-ignore a11y-mouse-events-have-key-events -->
<style>

    .wrapper{
        height: 100%;
    }

	img {
        width: 100%;
        height:auto;
        min-height: 200px;
    }
    .hoverbutton {
        position: absolute;
        background-color: rgba(0, 0, 0, 0.5);
        color: white;
        padding: 2.5% 2.5% 2.5% 2.5%;
        border: none;
        cursor: pointer;
        left: 5%;
    }

    .hoverbutton.top {
        top: 5%;
    }
    .hoverbutton.middle {
        top: 25%;
    }

    .hoverbutton.bottom {
        top: 45%;
    }

    .hoverbutton.furtherbottom {
        top: 65%;
    }

    .modal-background {
		position: fixed;
		display: flex;
		justify-content: center;
		align-items: center;
		left: 0;
		top: 0;
		width: 100%;
		height: 100%;
		backdrop-filter: blur(20px);
        z-index: 3;
	}

    .player{
        position: fixed;
		display: flex;
		justify-content: center;
		align-items: center;
		width: 65%;
		height: 65%;
        z-index: 4;
    }

    .large_image{
        position: fixed;
		display: flex;
		justify-content: center;
		align-items: center;
		width: 45%;
		height: 45%;
        z-index: 4;
    }

    .small_image {
        max-height: 240px;
    }

    .label {
        background-color: white;
        color: black; 
        border: 1px solid black;
        padding: 5px;
        margin: 5px;
        display: inline-block;
        transition: background-color 0.3s ease;
    }

    .label:hover {
        background-color: gray;
    }

    .image-labels {
        width: 10%;
    }

    .image-id {
        position: absolute;
        bottom: 2.5%;
        right: 1%;
        color: yellow;
        background: rgba(0, 0, 0, 0.5); 
        padding: 2px 5px;
    }

    .send-button {
      padding: 10px;
      margin: 10px;
    }

</style>


<!-- svelte-ignore a11y-click-events-have-key-events -->
<!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
<!-- svelte-ignore a11y-mouse-events-have-key-events -->

<svelte:window
    on:keydown={(e) => {
        if(video || large){
        logEvent("closePlayerWithKey", img.id);            
        }
        video = false;
        large = false;
    }}
/>
<!-- svelte-ignore a11y-click-events-have-key-events -->
<!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
<!-- svelte-ignore a11y-mouse-events-have-key-events -->
<!-- svelte-ignore a11y-no-static-element-interactions -->
<div class="wrapper" on:mouseover={() => (hover = true)}
    on:mouseout={() => (hover = false)}>
<img class="small_image {selected ? 'redBorder' : 'transparentBorder'}" src={"http://acheron.ms.mff.cuni.cz:42032/images/" + img.uri}
    alt="id: {img.id} score: {img.score}"
    on:click={imgClick} on:mouseover={() => (hover = true)}
    on:mouseout={() => (hover = false)} on:dblclick={largeImage} in:fade/>
{#if img.uri.split("/")[0] === 'LSC'}
<div class="image-id">{img.id[0].substring(6, 8)}. {img.id[0].substring(4, 6)}. {img.id[0].substring(0, 4)} {img.id[1].substring(0, 2)}:{img.id[1].substring(2, 4)}</div>
{/if}

{#if hover}
    <!-- svelte-ignore a11y-mouse-events-have-key-events -->
    <button style='--row_size:{row_size};' class="hoverbutton top" on:mouseover={() => (hover = true)} transition:fade on:click={send_result}>Send</button>
{/if}

{#if hover && $in_video_view && img.uri.split("/")[0] !== 'LSC'}
    <!-- svelte-ignore a11y-mouse-events-have-key-events -->
    <button style='--row_size:{row_size};' class="hoverbutton middle" on:mouseover={() => (hover = true)} transition:fade on:click={showVideo}>Video</button>
{/if}

{#if hover && !$in_video_view}
    <!-- svelte-ignore a11y-mouse-events-have-key-events -->
    <button style='--row_size:{row_size};' class="hoverbutton middle" on:mouseover={() => (hover = true)} transition:fade on:click={similarimage}>Similar</button>
    <!-- svelte-ignore a11y-mouse-events-have-key-events -->
    <button style='--row_size:{row_size};' class="hoverbutton bottom" on:mouseover={() => (hover = true)} transition:fade on:click={video_images}>Video Frames</button>
    {#if img.uri.split("/")[0] !== 'LSC'}
        <!-- svelte-ignore a11y-mouse-events-have-key-events -->
        <button style='--row_size:{row_size};' class="hoverbutton furtherbottom" on:mouseover={() => (hover = true)} transition:fade on:click={showVideo}>Video</button>
    {/if}
{/if}

</div>
<div bind:this={container}>
{#if video}
    <!-- svelte-ignore a11y-no-static-element-interactions -->
    <!-- svelte-ignore a11y-click-events-have-key-events -->
    <div class="modal-background" on:click|self={() => {
        video = false;
        logEvent("closePlayerWithMouse", img.id);
        }}>
        <div class="player">
            <VideoPlayer poster={"http://acheron.ms.mff.cuni.cz:42032/images/" + img.uri} source={"http://acheron.ms.mff.cuni.cz:42032/videos/" + img.uri.substring(0, img.uri.lastIndexOf('/')) + ".mp4"} />
            <Button class="send-button" color="secondary" on:click={send_result_videoframe} variant="raised">
                Send Frame
            </Button>
        </div>
    </div>
{/if}
</div>
{#if large}
    <!-- svelte-ignore a11y-no-static-element-interactions -->
    <!-- svelte-ignore a11y-click-events-have-key-events -->
    <div class="modal-background" on:click|self={() => {
        large = false;
        logEvent("closeLargeWithMouse", img.id);
        }}>
        <div class="large_image">
            <!-- svelte-ignore a11y-click-events-have-key-events -->
            <!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
            <!-- svelte-ignore a11y-mouse-events-have-key-events -->
            <img class="{selected ? 'redBorder' : 'transparentBorder'}" src={"http://acheron.ms.mff.cuni.cz:42032/images/" + img.uri.split("/")[0] + (img.uri.split("/")[0] === 'LSC' ? "/large/" : "/") + img.uri.split("/").slice(1).join("/")}
            alt="id: {img.id} score: {img.score}"
            on:click={imgClick} in:fade/>
            <div class="image-labels">
                {#each labels || [] as label}
                    <button class="label" on:click={() => add_label_to_query(label)}>{label}</button>
                {/each}
            </div>
        </div>
    </div>
{/if}
