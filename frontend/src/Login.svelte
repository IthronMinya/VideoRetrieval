<script>
    import { createEventDispatcher } from 'svelte';

    import { is_login, password, username } from './stores';

    import CryptoJS from 'crypto-js';

    const dispatch = createEventDispatcher();

    let passw = '';
    let errorMessage = '';

    // Access the secret key from the environment variables
    const secretKey = import.meta.env.VITE_SECRET_KEY;

    let users = [...Array.from({ length: 10 }, (_, i) => `prak_novice${String(i + 1)}`), ...Array.from({ length: 9 }, (_, i) => `06prak${String(i + 1)}`), "prak_test", ...Array.from({ length: 20 }, (_, i) => `user${String(i + 1).padStart(2, '0')}`)];
    let consentGiven = false;
  
    async function login() {
        if (!consentGiven) {
            errorMessage = "You must agree to data collection before logging in.";
            return;
        }

	    try {
            // Encrypt the password
            const encryptedPassword = CryptoJS.AES.encrypt(passw, secretKey).toString();

            const response = await fetch(`${window.location.origin}/login`, {
                method: 'POST',
                headers: {
                'Content-Type': 'application/json',
                },
                body: JSON.stringify({ "username": $username, "password": encryptedPassword }),
            });

            if (response.ok) {
                const data = await response.json();
                $password = data;
                $is_login = true;
                // set username in cookie for future use
                document.cookie = `username=${$username};`;
                document.cookie = `tags=${$password};`;
                dispatch('loginSuccess');
            } else {
                const errorData = await response.json();
                errorMessage = errorData.message || 'Login failed';
            }
        } catch (error) {
            errorMessage = 'Network error. Please try again later.';
        }
    }
</script>

<style>
    .container {
        max-width: 400px;
        margin: 0 auto;
        padding: 2rem;
        background-color: #fff;
        border-radius: 0.5rem;
        box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
    }
    .error-message {
        color: red;
        margin-top: 1rem;
    }
</style>

<div class="container">
    <h2 class="text-2xl font-bold mb-4">Login for {$username}</h2>
    <form on:submit|preventDefault={login} class="space-y-4">
        <div>
            <label for="username" class="block text-sm font-medium text-gray-700">Username</label>
            <br/>
            <select id="username" bind:value={$username} class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm">
                <option value="" disabled selected>Select a user</option>
                {#each users as user}
                    <option value={user}>{user}</option>
                {/each}
            </select>
        </div>
        <div>
            <label for="password" class="block text-sm font-medium text-gray-700">Password</label>
            <br/>
            <input id="password" type="password" bind:value={passw} class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm" />
        </div>
        <div>
	    <input type="checkbox" id="consent" bind:checked={consentGiven} />
	    <label for="consent" class="ml-2 text-sm text-gray-700">I agree to the collection of anonymous usage data for testing and research purposes.</label>
	</div>
        {#if errorMessage}
            <p class="error-message">{errorMessage}</p>
        {/if}
        <br/>
        <button type="submit" class="w-full py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">Login</button>
    </form>
</div>
  
