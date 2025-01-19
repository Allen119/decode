<template>
  <div id="app" class="font-moulpali h-screen w-screen" :style="{
    //background: 'linear-gradient(135deg, rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.9))',
    background: 'linear-gradient(135deg, #000000, #262222)'
  }">
    <!-- Left Image -->
    <img src="@/assets/images/log.gif" alt="Left Image" class="absolute left-0 h-full" :style="{
      width: '45.63%',
      height: '100%', /* Custom width since Tailwind doesn't support decimals directly */
    }" />
    <div class="absolute bg-white shadow-lg" :style="{
      width: '41.67%',
      height: '61.62%',
      top: '19.24%',
      right: '6.0%',
      background: 'linear-gradient(135deg, #000000, #262222)'
      /* Apply the gradient here */
    }">
      <!-- Centered Text at the Top -->
      <p class="absolute text-center text-white text-[30px] top-[16%] w-full">
        CODE CAMPUS
      </p>

      <!-- Content inside the container -->
      <div class="flex justify-center items-center h-full">
        <form class="p-6 space-y-4 w-full max-w-[600px]">
          <!-- Email Input -->
          <div>
            <label for="email" class="block text-white font-medium">Email</label>
            <input type="email" id="email" name="email"
              class="w-full h-[70px] bg-gray-800 text-gray-700 px-4 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-black focus:text-white placeholder:text-gray-500"
              placeholder="Enter your email" required />
          </div>

          <!-- Password Input -->
          <div>
            <label for="password" class="block text-white font-medium">Password</label>
            <input type="password" id="password" name="password"
              class="w-full h-[70px] bg-gray-800 text-gray-700 px-4 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-black focus:text-white placeholder:text-gray-500"
              placeholder="Enter your password" required />
          </div>


          <!-- Login Button -->
          <div>
            <button type="submit"
              class="w-[239px] h-[60px] bg-[#7DE5F4] text-white py-2 rounded hover:bg-[#227380] transition duration-200 transform translate-x-[0%] translate-y-[12%]">
              Login
            </button>
          </div>

          <!-- "Do you already have an account?" text placed on the right side of the button -->
          <div class="absolute right-[16%] top-[61%] text-gray-800 text-[16px]">
            Don't have an account?<br>Please use the
            <span @click="navigateTo('/register')" class="text-[#7DE5F4] hover:text-[#5CC7E8] cursor-pointer">
              Register
            </span>
          </div>
        </form>
      </div>
    </div>

  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';


const router = useRouter();

const navigateTo = (path) => {
  router.push(path);
};
</script>
