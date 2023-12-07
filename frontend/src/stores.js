import { writable } from 'svelte/store';

export let selected_images = writable([]);
export let scroll_height = writable(0);
export let in_video_view = writable(false);
