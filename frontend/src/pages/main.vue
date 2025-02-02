<template>
  <div id="app">
    <!-- Left Sidebar -->
    <div class="absolute shadow-lg flex flex-col justify-start items-center" :style="{
      width: '16.8%', /* Sidebar width */
      height: '100vh', /* Full height of the viewport */
      top: '0',
      left: '0',
      background: 'rgba(217, 106, 106, 1)'
    }">

      <!-- Inner Box at Top of Sidebar -->
      <div class="w-full flex items-center px-4 hover:border-2" :style="{
        height: '7%',
        backgroundColor: 'rgba(217, 217, 217, 1)',
        borderColor: 'rgba(45, 46, 79, 0.35)',
        transition: 'border-color 0.3s ease',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
      }">
        <!-- Image -->
        <img src="@/assets/images/Ellipse1.png" alt="Left Image" :style="{
          width: '30px',
          height: '30px',
          transform: 'translateX(-80px) translateY(15px)'
        }" />
        <!-- Centered Paragraph -->
        <p class="text-[20px] font-light text-black" :style="{
          transform: 'translateY(-15px)'
        }">
          PKD21IT009
        </p>
      </div>

      <!-- Customizable Boxes -->
      <div
        class="absolute shadow-lg flex flex-col justify-start items-center overflow-y-auto scrollbar scrollbar-thumb-gray-400 scrollbar-track-gray-200"
        :style="{
          width: '100%', /* Sidebar width */
          height: '100%', /* Full height of the viewport */
          top: '7%',
          left: '0',
          background: 'rgba(255, 255, 255, 1)'
        }">
        <!-- Boxes -->
        <div v-for="(box, index) in boxes" :key="box.id" :id="`box-${box.id}`" :data-index="index"
          class="w-full flex items-center px-4 cursor-pointer" :style="{
            height: box.height,
            width: box.width,
            backgroundColor: box.backgroundColor || 'rgba(217, 217, 217, 0.9)',
            transition: 'border-color 0.3s ease',
            marginTop: box.marginTop,
            justifyContent: 'center',
            borderRadius: box.borderRadius,
            border: box.border,
            position: box.position,
            fontSize: box.fontSize || '16px',
            transform: box.transform
          }" @click="handleBoxClick(box)">
          <!-- Logo Image on Left Side -->
          <img :src="box.logo" alt="Logo" :style="box.logoStyle" />

          <!-- Box Text -->
          <p class="font-light text-black mx-auto" :style="box.textStyle">
            {{ box.name }}
          </p>
        </div>

        <!-- Horizontal Line -->
        <div class="w-[100%] h-[2px] bg-gray-500 mt-10 mb-2"></div>

        <p class="text-xl font-bold mt-4 mb-4 transform translate-y-2 translate-x-[-71%]">
          Explore More
        </p>

        <!-- Explore Boxes -->
        <div v-for="(box, index) in explorebox" :key="box.id" :id="`box-${box.id}`" :data-index="index"
          class="w-full flex items-center px-4 cursor-pointer" :style="{
            height: box.height,
            width: box.width,
            backgroundColor: box.backgroundColor || 'rgba(217, 217, 217, 0.9)',
            transition: 'border-color 0.3s ease',
            marginTop: box.marginTop,
            justifyContent: 'center',
            borderRadius: box.borderRadius,
            position: box.position,
            fontSize: box.fontSize || '16px',
            transform: box.transform
          }" @click="handleBoxClick(box)">
          <!-- Logo Image on Left Side -->
          <img :src="box.logo" alt="Logo" :style="box.logoStyle" />

          <!-- Box Text -->
          <p class="font-light text-black mx-auto" :style="box.textStyle">
            {{ box.name }}
          </p>
        </div>
      </div>

    </div>



    <!-- Top Bar -->
    <div class="absolute shadow-lg flex flex-col justify-center items-center" :style="{
      width: '82.58%',
      height: '7%',
      top: '0',
      left: '17.42%',
      background: 'rgba(217, 217, 217, 1)',
    }">
      <!-- Logo -->
      <img src="@/assets/images/logo.png" alt="Vertically Centered Image" class="object-contain" :style="{
        maxHeight: '80%',
        position: 'absolute',
        top: '50%',
        left: '80px',
        transform: 'translateY(-50%)',
      }" />

      <!-- Form Input Box -->
      <input type="text" placeholder="Search File & Courses"
        class="border border-gray-300 rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-[rgba(217,217,217,1)] text-[rgba(217,217,217,1)] text-center"
        :style="{
          width: '60%', /* Adjust width */
          height: '58%', /* Adjust height */
          textAlign: 'center', /* Horizontally center placeholder text */
          lineHeight: '2.5', /* Vertically center placeholder text (match it to input height if needed) */
        }" />
    </div>




    <!-- Main Content Area -->
    <div class="absolute shadow-lg flex flex-col justify-center items-center transition-all duration-100"
      :class="{ 'blur-sm': showContainer }" :style="{
        width: '82.58%',
        height: '100vh',
        top: '7%',
        left: '17.42%',
        background: 'rgba(217, 217, 217, 1)'
      }">
      <img src="@/assets/images/createjoin.svg" alt="Centered Image"
        class="object-contain cursor-pointer hover:opacity-80" :style="{
          maxWidth: '80%',
          maxHeight: '80%'
        }" @click="performAction" />

      <p class="text-[20px] font-bold mt-4 mb-4 transform translate-y-[100px] translate-x-[-579%]">
        Recent files
      </p>

      <!-- Boxes -->
      <div v-for="(box, index) in recentbox" :key="box.id" :id="`box-${box.id}`" :data-index="index"
        class="w-full flex items-center px-4 cursor-pointer" :style="{
          top: '5%',
          height: box.height,
          width: box.width,
          backgroundColor: box.backgroundColor || 'rgba(217, 217, 217, 0.9)',
          transition: 'border-color 0.3s ease',
          marginTop: box.marginTop,
          justifyContent: 'center',
          borderRadius: box.borderRadius,
          border: box.border,
          position: box.position,
          fontSize: box.fontSize || '20px',
          transform: box.transform
        }" @click="handleBoxClick(box)">
        <p class="font-light text-black mx-auto" :style="box.textStyle">
          {{ box.name }}
        </p>
      </div>
    </div>

    <!-- Button to toggle container (Outside main content area) -->
    <button @click="toggleContainer"
      class="absolute right-12 bg-[rgba(40,41,71,1)] text-white font-bold rounded-[7px] hover:opacity-90 focus:outline-none w-36 h-12 flex items-center justify-center transform translate-y-[10px]">
      <div class="flex items-center space-x-2">
        <img src="@/assets/images/plus.svg" alt="Icon" class="w-6 h-6 rounded-full object-contain" />
        <span>Create File</span>
      </div>
    </button>


    <!-- New Container (Outside main content area) -->
    <div v-if="showContainer" ref="containerRef"
    class="absolute top-20 right-12 w-[450px] h-[80px] bg-[rgba(217,217,217,1)] rounded-md shadow-lg flex items-center justify-center z-50 transform translate-y-2">
    <div class="flex items-center justify-center w-full space-x-4">
      <!-- Input Box -->
      <input 
        type="text" 
        v-model="fileName" 
        placeholder="Enter file name" 
        class="w-[300px] h-[40px] p-2 rounded-md border-2 border-gray-300" 
      />

      <!-- Save Button -->
      <button 
        @click="saveFile"
        class="w-[100px] h-[40px] bg-[rgba(40,41,71,1)] text-white rounded-md hover:bg-[#797a9c]">
        Save
      </button>
    </div>
  </div>




  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import plusLogo from '@/assets/images/plus.svg';
import gitLogo from '@/assets/images/GitHub.svg';
import Homelog from '@/assets/images/Homelog.svg';
import files from '@/assets/images/filess.svg';
import project from '@/assets/images/projects.svg';
import course from '@/assets/images/course.svg';
import profile from '@/assets/images/profile.svg';
import documentation from '@/assets/images/documentation.svg';
import settings from '@/assets/images/Settings.svg';
import help from '@/assets/images/Help.svg';

import { useRouter } from "vue-router";

const router = useRouter(); // Initialize the router instance

const navigateTo = (path) => {
  router.push(path); // Use the router instance to navigate
};


// Dynamically managed boxes with custom styles
const boxes = ref([
  {
    id: 1,
    name: 'Create project',
    logo: plusLogo,
    height: '5%',
    width: '94%',
    backgroundColor: 'rgba(255, 255, 255, 1)',
    border: '1px solid rgba(45, 46, 79, 0.35)',
    borderRadius: '7px',
    position: 'relative',
    marginTop: '20px',
    fontSize: '20px',
    logoStyle: { width: '22px', height: '22px', marginRight: '15px', transform: 'translateY(0px) translateX(40px)' },
    textStyle: { transform: 'translateX(-20px)' }
  },
  // {
  //   id: 2,
  //   name: 'Import from GitHub',
  //   logo: gitLogo,
  //   height: '5%',
  //   width: '94%',
  //   border: '1px solid rgba(45, 46, 79, 0.35)',
  //   backgroundColor: 'rgba(255, 255, 255, 1)',
  //   borderRadius: '7px',
  //   position: 'relative',
  //   marginTop: '20px',
  //   fontSize: '20px',
  //   logoStyle: { width: '40px', height: '40px', marginRight: '15px', transform: 'translateX(30px)' },
  //   textStyle: { transform: 'translateX(-10px)' }
  // },
  {
    id: 3,
    name: 'Home',
    logo: Homelog,
    height: '4%',
    width: '37%',
    backgroundColor: 'rgba(255, 255, 255, 1)',
    //border: '1px solid rgba(45, 46, 79, 0.35)',
    borderRadius: '7px',
    position: 'relative',
    marginTop: '24px',
    fontSize: '20px',
    logoStyle: { width: '30px', height: '30px', marginRight: '10%', transform: 'translateX(-6.5px) translateY(-1.5px)' },
    transform: 'translateX(-93px)',
    textStyle: { transform: 'translateX(-6px)' }
  },
  {
    id: 4,
    name: 'Files',
    logo: files,
    height: '4%',
    width: '37%',
    backgroundColor: 'rgba(255, 255, 255, 1)',
    borderRadius: '7px',
    position: 'relative',
    marginTop: '24px',
    fontSize: '20px',
    logoStyle: { width: '30px', height: '30px', marginRight: '15px', transform: 'translateX(-8px) translateY(0px)' },
    transform: 'translateX(-93px)',
    textStyle: { transform: 'translateX(-17.5px)' }
  },
  {
    id: 5,
    name: 'Projects',
    logo: project,
    height: '4%',
    width: '37%',
    backgroundColor: 'rgba(255, 255, 255, 1)',
    borderRadius: '7px',
    position: 'relative',
    marginTop: '24px',
    fontSize: '20px',
    logoStyle: { width: '30px', height: '30px', marginRight: '15px', transform: 'translateX(5px) translateY(0px)' },
    transform: 'translateX(-93px)',
    textStyle: { transform: 'translateX(0px)' }
  },
  {
    id: 6,
    name: 'Courses',
    logo: course,
    height: '4%',
    width: '37%',
    backgroundColor: 'rgba(255, 255, 255, 1)',
    borderRadius: '7px',
    position: 'relative',
    marginTop: '24px',
    fontSize: '20px',
    logoStyle: { width: '30px', height: '30px', marginRight: '15px', transform: 'translateX(5px) translateY(0px)' },
    transform: 'translateX(-93px)',
    textStyle: { transform: 'translateX(0px)' }
  },
  {
    id: 7,
    name: 'Profile',
    logo: profile,
    height: '4%',
    width: '37%',
    backgroundColor: 'rgba(255, 255, 255, 1)',
    borderRadius: '7px',
    position: 'relative',
    marginTop: '24px',
    fontSize: '20px',
    logoStyle: { width: '30px', height: '30px', marginRight: '15px', transform: 'translateX(-3px) translateY(0px)' },
    transform: 'translateX(-93px)',
    textStyle: { transform: 'translateX(-7.5px)' }
  },
]);

const explorebox = ref([
  {
    id: 1,
    name: 'Documentation',
    logo: documentation,
    height: '4%',
    width: '60%',
    backgroundColor: 'rgba(255, 255, 255, 1)',
    borderRadius: '7px',
    position: 'relative',
    marginTop: '24px',
    fontSize: '20px',
    logoStyle: { width: '30px', height: '30px', marginRight: '10px', transform: 'translateX(-2px) translateY(0px)' },
    transform: 'translateX(-55.0px)',
    textStyle: { transform: 'translateX(-3px)' }
  },
  {
    id: 4,
    name: 'Settings',
    logo: settings,
    height: '4%',
    width: '37%',
    backgroundColor: 'rgba(255, 255, 255, 1)',
    borderRadius: '7px',
    position: 'relative',
    marginTop: '24px',
    fontSize: '20px',
    logoStyle: { width: '30px', height: '30px', marginRight: '15px', transform: 'translateX(7.5px) translateY(0px)' },
    transform: 'translateX(-93px)',
    textStyle: { transform: 'translateX(1px)' }
  },
  {
    id: 5,
    name: 'Help',
    logo: help,
    height: '4%',
    width: '37%',
    backgroundColor: 'rgba(255, 255, 255, 1)',
    borderRadius: '7px',
    position: 'relative',
    marginTop: '24px',
    fontSize: '20px',
    transform: 'translateX(-93px)',
    logoStyle: { width: '30px', height: '30px', marginRight: '15px', transform: 'translateX(-5.5px) translateY(0px)' },
    textStyle: { transform: 'translateX(-15px)' }
  },
]);

const recentbox = ref([
  {
    id: 1,
    name: 'File 1',
    //logo: documentation,
    height: '5%',
    width: '85%',
    backgroundColor: 'rgba(217, 217, 217, 1)',
    border: '0.5px solid rgba(45, 46, 79, 0.35)',
    borderRadius: '14px',
    position: 'relative',
    marginTop: '24px',
    fontSize: '20px',
    logoStyle: { width: '30px', height: '30px', marginRight: '10px', transform: 'translateX(-2px) translateY(0px)' },
    transform: 'translateX(-55px) translateY(30px)',
    textStyle: { transform: 'translateX(-570px)' }
  },
  {
    id: 2,
    name: 'File 2',
    //logo: settings,
    height: '5%',
    width: '85%',
    backgroundColor: 'rgba(217, 217, 217, 1)',
    border: '0.5px solid rgba(45, 46, 79, 0.35)',
    borderRadius: '14px',
    position: 'relative',
    marginTop: '24px',
    fontSize: '20px',
    logoStyle: { width: '30px', height: '30px', marginRight: '15px', transform: 'translateX(7.5px) translateY(0px)' },
    transform: 'translateX(-55px) translateY(30px)',
    textStyle: { transform: 'translateX(-570px)' }
  },

  {
    id: 3,
    name: 'Course 1',
    //logo: settings,
    height: '5%',
    width: '85%',
    backgroundColor: 'rgba(217, 217, 217, 1)',
    border: '0.5px solid rgba(45, 46, 79, 0.35)',
    borderRadius: '14px',
    position: 'relative',
    marginTop: '24px',
    fontSize: '20px',
    logoStyle: { width: '30px', height: '30px', marginRight: '15px', transform: 'translateX(7.5px) translateY(0px)' },
    transform: 'translateX(-55px) translateY(30px)',
    textStyle: { transform: 'translateX(-570px)' }
  },

  {
    id: 4,
    name: 'Course 2',
    //logo: settings,
    height: '5%',
    width: '85%',
    backgroundColor: 'rgba(217, 217, 217, 1)',
    border: '0.5px solid rgba(45, 46, 79, 0.35)',
    borderRadius: '14px',
    position: 'relative',
    marginTop: '24px',
    fontSize: '20px',
    logoStyle: { width: '30px', height: '30px', marginRight: '15px', transform: 'translateX(7.5px) translateY(0px)' },
    transform: 'translateX(-55px) translateY(30px)',
    textStyle: { transform: 'translateX(-570px)' }
  },
  // {
  //   id: 5,
  //   name: 'Help',
  //   logo: help,
  //   height: '4%',
  //   width: '37%',
  //   backgroundColor: 'rgba(255, 255, 255, 1)',
  //   borderRadius: '7px',
  //   position: 'relative',
  //   marginTop: '24px',
  //   fontSize: '20px',
  //   transform: 'translateX(-93px)',
  //   logoStyle: { width: '30px', height: '30px', marginRight: '15px', transform: 'translateX(-5.5px) translateY(0px)' },
  //   textStyle: { transform: 'translateX(-15px)' }
  // },
]);

function handleBoxClick(box) {
  console.log('Box clicked:', box);
  // Add your custom logic here, e.g., navigation, modal, etc.
}
const performAction = () => {
  console.log('Clicked');
  // Add your custom logic here, e.g., navigating to a new route or triggering a modal
  //alert('Action performed!');
};

const fileName = ref(""); // Holds the input file name
const showContainer = ref(false)
const containerRef = ref(null)
const saveError = ref(""); // Holds error messages

const toggleContainer = () => {
  showContainer.value = !showContainer.value
}

const handleClickOutside = (event) => {
  if (
    showContainer.value &&
    containerRef.value &&
    !containerRef.value.contains(event.target) &&
    !event.target.closest('button')
  ) {
    showContainer.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

const saveFile = async () => {
  if (!fileName.value.trim()) {
    saveError.value = "Please enter a file name.";
    return;
  }

  // Determine the language based on the file extension
  const language = fileName.value.endsWith(".py") ? "Python" : "Unknown";

  try {
    const response = await fetch("http://decode.local:8080/api/method/decode.api.codingFiles", {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        file_name: fileName.value,
        language: language,
        code: "", // Include code content if needed
      }),
    });

    const data = await response.json();
    console.log("Full API Response:", data);

    if (data.message) {
      alert(data.message.message); // Show success message
      console.log("User Document:", data.message.user);
      const lastFileUuid = data.message.user.codingfiles[data.message.user.codingfiles.length - 1].name;
      
      // Navigate to filecode with the UUID
      router.push(`/filecode/${lastFileUuid}`);
    } else {
      saveError.value = "An unexpected error occurred.";
    }
  } catch (error) {
    console.error("Save file error:", error);
    saveError.value = "Failed to save the file. Please try again.";
  }

  // Clear the file name input
  fileName.value = "";
};
</script>

<style scoped>
/* Apply Inter font to the entire component */
body {
  font-family: 'Inter', sans-serif;
}

/* Optional: Keep the .font-inter class if needed for specific overrides */
.font-inter {
  font-family: 'Inter', sans-serif;
}
</style>

