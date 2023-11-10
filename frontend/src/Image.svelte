<script>
    import { selected_images } from './stores.js';
    import { fade } from 'svelte/transition';
    import VideoPlayer from 'svelte-video-player';

    export let img;

    const poster = 'https://www.server.com/poster.jpg';
    const source = 'https://www.server.com/video.mp4';


    let selected = $selected_images.includes(img.id);
    let hover = false;
    let video = false;

    function showVideo(){
        video = true;
    }

    function imgClick() {

        if (!selected){
            $selected_images = [...$selected_images, img.id];

        }else{
            $selected_images=$selected_images.filter(e => e !== img.id);
        }

        selected = !selected;

        console.log($selected_images);
    }
</script>

<style>
	img {
        max-width: 100%;
        height: 12em;   
    }
    .hoverbuttontop{
        position: absolute;
        top: 35%;
        left: 50%;
        transform: translate(-50%, -35%);
        background-color: rgba(0, 0, 0, 0.5);
        color: white;
        padding: 10px 20px;
        border: none;
        cursor: pointer;
    }

    .hoverbuttonbottom{
        position: absolute;
        top: 65%;
        left: 50%;
        transform: translate(-50%, -65%);
        background-color: rgba(0, 0, 0, 0.5);
        color: white;
        padding: 10px 20px;
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
		width: 85%;
        margin-left: 15%;
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

</style>


<!-- svelte-ignore a11y-click-events-have-key-events -->
<!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
<!-- svelte-ignore a11y-mouse-events-have-key-events -->

<img class="{selected ? 'redBorder' : 'transparentBorder'}" src={"http://acheron.ms.mff.cuni.cz:42032/images/" + img.uri}
    alt="id: {img.id} score: {img.score}"
    on:click={imgClick} on:mouseover={() => (hover = true)}
    on:mouseout={() => (hover = false)} in:fade/>

{#if hover}
    <button class="hoverbuttontop" transition:fade>Send</button>
    <button class="hoverbuttonbottom" transition:fade on:click={showVideo}>Show Video</button>
{/if}
{#if video}
    <!-- svelte-ignore a11y-no-static-element-interactions -->
    <div class="modal-background" on:click|self={() => video = false}
        on:keydown={(e) => {
            console.log("test");
            if (e.key === 'Escape') video = false;
        }}>
        <div class="player">
            <VideoPlayer {poster} {source} />
        </div>
    </div>
{/if}