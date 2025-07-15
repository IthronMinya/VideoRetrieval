<script>
    import Image from './Image.svelte';
    import { logEvent } from './Logger.js';
    import { selected_images } from './stores.js';
    import { createEventDispatcher } from 'svelte';
    export let row;
    export let row_size;
    export let labels;
    let images = [];

    // variables used for limiting the number of logging callbacks when scrolling
    const throttleDelay = 200;
    let lastScroll = 0;

    const dispatch = createEventDispatcher()

    function similarimage(image_id){

        dispatch('similarimage', {image_id});
    }

    function video_images(image_id){

        dispatch('video_images', {image_id});
    }

    function send_result(image_id){
        dispatch('send_result', {image_id});
    }

    function logScroll(video_id) {
        const now = Date.now();
        if (now - lastScroll >= throttleDelay) {
            logEvent("horizontalScroll", video_id);
            lastScroll = now;
        }
    }

    function send_result_videoframe(event, image_id){
        let video_time = event.detail.video_time;
        dispatch('send_result_videoframe', {video_time, image_id});
    }

</script>

<style>
	.row {
        display: flex;
        flex-wrap: nowrap;
        box-sizing: border-box;
        overflow-x: auto;
        scrollbar-width: none; /* For Firefox */
        -ms-overflow-style: none;  /* For Internet Explorer and Edge */
    }

    .row::-webkit-scrollbar { /* For Chrome, Safari and Opera */
        display: none;
    }

    .item {
        box-sizing: border-box; /* Account for padding and margin */
        flex: 0 0 auto;
        position: relative;
        width: calc(100% / var(--row_size) );
    }

    
</style>

<div class="row" style='--row_size:{row_size};--row_items:{row.length};' on:scroll={(event) => logScroll(row[0].id[0])}>
	{#each row as img, index}
        <div class="item">
            <Image bind:this={images[index]} on:send_result_videoframe={(video_time) => send_result_videoframe(video_time, img.id)} on:send_result={() => send_result(img.id)} on:similarimage={() => similarimage(img.id)} on:video_images={() => video_images(img.id)} {img} row_size={row.length} selected={$selected_images.includes(img.id)} labels={img.label.map(i => labels[i])}/>
        </div>
	{/each}
</div>

    
