<script>
    import { selected_images } from './stores.js';
    import { fade } from 'svelte/transition';
    import VideoPlayer from 'svelte-video-player';
    import { createEventDispatcher } from 'svelte'
    const dispatch = createEventDispatcher()

    export let img;
    export let row_size;

    const poster = 'https://www.server.com/poster.jpg';
    const source = 'https://www.server.com/video.mp4';

    export let selected;
    let hover = false;
    let video = false;
    let large = false;
    
    function showVideo(){
        video = true;
    }

    function largeImage(){
        large = true;
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

    export function imgClick() {

        if (!selected){
            $selected_images = [...$selected_images, img.id];

        }else{
            $selected_images=$selected_images.filter(e => e !== img.id);
        }

        selected = !selected;

        console.log($selected_images);
    }
</script>

<!-- svelte-ignore a11y-mouse-events-have-key-events -->
<style>
	img {
        width: 100%;
        height: auto;
    }
    .hoverbuttontop{
        position: absolute;
        top: 5%;
        left: 5%;
        background-color: rgba(0, 0, 0, 0.5);
        color: white;
        padding: 2.5% 2.5% 2.5% 2.5%;
        border: none;
        cursor: pointer;
    }

    .hoverbuttonmiddle{
        position: absolute;
        top: 25%;
        left: 5%;
        background-color: rgba(0, 0, 0, 0.5);
        color: white;
        padding: 2.5% 2.5% 2.5% 2.5%;
        border: none;
        cursor: pointer;
    }

    .hoverbuttonbottom{
        position: absolute;
        top: 45%;
        left: 5%;
        background-color: rgba(0, 0, 0, 0.5);
        color: white;
        padding: 2.5% 2.5% 2.5% 2.5%;
        border: none;
        cursor: pointer;
    }

    .hoverbuttonfurtherbottom{
        position: absolute;
        top: 65%;
        left: 5%;
        background-color: rgba(0, 0, 0, 0.5);
        color: white;
        padding: 2.5% 2.5% 2.5% 2.5%;
        border: none;
        cursor: pointer;
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
		width: 35%;
		height: 35%;
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

</style>


<!-- svelte-ignore a11y-click-events-have-key-events -->
<!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
<!-- svelte-ignore a11y-mouse-events-have-key-events -->

<svelte:window
    on:keydown={(e) => {
        video = false;
        large = false;
    }}
/>
<!-- svelte-ignore a11y-click-events-have-key-events -->
<!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
<!-- svelte-ignore a11y-mouse-events-have-key-events -->
<img class="{selected ? 'redBorder' : 'transparentBorder'}" src={"http://acheron.ms.mff.cuni.cz:42032/images/" + img.uri}
    alt="id: {img.id} score: {img.score}"
    on:click={imgClick} on:mouseover={() => (hover = true)}
    on:mouseout={() => (hover = false)} on:dblclick={largeImage} in:fade/>

{#if hover}
    <!-- svelte-ignore a11y-mouse-events-have-key-events -->
    <button style='--row_size:{row_size};' class="hoverbuttontop" on:mouseover={() => (hover = true)} transition:fade on:click={send_result}>Send</button>
    <!-- svelte-ignore a11y-mouse-events-have-key-events -->
    <button style='--row_size:{row_size};' class="hoverbuttonmiddle" on:mouseover={() => (hover = true)} transition:fade on:click={similarimage}>Similar To This</button>
    <!-- svelte-ignore a11y-mouse-events-have-key-events -->
    <button style='--row_size:{row_size};' class="hoverbuttonbottom" on:mouseover={() => (hover = true)} transition:fade on:click={showVideo}>Show Video</button>
    <!-- svelte-ignore a11y-mouse-events-have-key-events -->
    <button style='--row_size:{row_size};' class="hoverbuttonfurtherbottom" on:mouseover={() => (hover = true)} transition:fade on:click={video_images}>Show Nearby Frames</button>
{/if}
{#if video}
    <!-- svelte-ignore a11y-no-static-element-interactions -->
    <!-- svelte-ignore a11y-click-events-have-key-events -->
    <div class="modal-background" on:click|self={() => video = false}>
        <div class="player">
            <VideoPlayer {poster} {source} />
        </div>
    </div>
{/if}
{#if large}
    <!-- svelte-ignore a11y-no-static-element-interactions -->
    <!-- svelte-ignore a11y-click-events-have-key-events -->
    <div class="modal-background" on:click|self={() => large = false}>
        <div class="large_image">
            <!-- svelte-ignore a11y-click-events-have-key-events -->
            <!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
            <!-- svelte-ignore a11y-mouse-events-have-key-events -->
            <img class="{selected ? 'redBorder' : 'transparentBorder'}" src={"http://acheron.ms.mff.cuni.cz:42032/images/" + img.uri}
            alt="id: {img.id} score: {img.score}"
            on:click={imgClick} in:fade/>
        </div>
    </div>
{/if}