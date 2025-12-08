/**
 * User Store - Manages user profile and settings
 * Zustand store for user data including class level, subject preferences, etc.
 */

import { create } from "zustand";
import { persist } from "zustand/middleware";

/**
 * User Store
 * 
 * TODO: Backend Integration
 * - Load user profile from API on login
 * - Save preferences to backend
 * - Sync across devices
 */

const useUserStore = create(
  persist(
    (set, get) => ({
      // User Profile
      user: {
        id: null,
        name: "",
        email: "",
        classLevel: 6, // Default to Class 6
        preferredSubject: "Mathematics",
      },

      // Authentication state
      isAuthenticated: false,

      // Actions
      setUser: (userData) => set({ user: userData, isAuthenticated: true }),

      setClassLevel: (classLevel) =>
        set((state) => ({
          user: { ...state.user, classLevel },
        })),

      setPreferredSubject: (subject) =>
        set((state) => ({
          user: { ...state.user, preferredSubject: subject },
        })),

      logout: () =>
        set({
          user: {
            id: null,
            name: "",
            email: "",
            classLevel: 6,
            preferredSubject: "Mathematics",
          },
          isAuthenticated: false,
        }),

      // Get current class level
      getClassLevel: () => get().user.classLevel,

      // Get current subject
      getSubject: () => get().user.preferredSubject,
    }),
    {
      name: "user-storage", // LocalStorage key
      skipHydration: false, // Enable hydration
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

export default useUserStore;
