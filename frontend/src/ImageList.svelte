<script>
    import Image from './Image.svelte';
    export let row;
</script>

<style>
	.row {
        display: table;
        border-collapse: collapse;
        width: 100%;
    }
    .item {
        display: table-cell;
        vertical-align: top;
        padding: 5px;
        position: relative;
        width: 20%;
    }
</style>

<div class="row">
	{#each row as img, index}
        <div class="item">
            <Image {img}/>
        </div>
	{/each}
</div>

    
