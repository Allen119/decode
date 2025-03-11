<template>
    <div id="app" class="font-sans h-screen w-screen bg-white text-white flex flex-col">
        <!-- Header -->
        <header class="bg-[rgba(217,217,217,1)] text-purple-700 p-4 flex justify-between items-center h-[7%] relative"
            :style="{ fontFamily: 'Inter, sans-serif' }">
            <!-- Logo and User ID Section -->
            <div class="flex items-center gap-4">
                <img src="@/assets/images/logo.png" alt="Logo" class="object-contain"
                    :style="{ maxHeight: '80%', width: '10%', height: 'auto' }" />
                <span class="text-[150%] text-black">Hi {{ userName }} welcome back</span>
            </div>

            <!-- Course Name (Centered and 30% from the left) -->
            <p class="absolute text-[150%] right-[10%] top-1/2 transform -translate-y-1/2 text-lg text-black font-extralight"
                :style="{ fontFamily: 'Inter, sans-serif', fontWeight: 200 }">
                {{ courseName }}hjhj
            </p>


        </header>

        <div class="absolute bg-[#D9D9D9] w-[52%] h-[87%] top-[10%] right-[47%]"></div>
        <div class="absolute bg-[#D9D9D9] w-[40%] h-[75%] top-[16%] right-[3.5%] rounded-[74px]">
            <div class="absolute bg-[#D9D9D9] w-[40%] h-[75%] top-[16%] right-[3.5%] rounded-[74px]">

            </div>
        </div>
    </div>
</template>

<script>


</script>