import { lessons as lessonPDFs } from "../assets/index.js";

/**
 * Lessons Configuration - Class 6 Mathematics
 *
 * TODO: Move this to backend API
 * Replace static data with dynamic API call: GET /api/lessons
 *
 * Backend should return:
 * - Lesson metadata (id, title, description, number)
 * - PDF URLs (from cloud storage like S3, Azure Blob, etc.)
 * - Additional fields (author, duration, difficulty, tags, etc.)
 */

export const SAMPLE_LESSONS = [
  {
    id: 1,
    number: 1,
    title: "Knowing Our Numbers",
    description:
      "Understanding large numbers, estimation, comparison, and place value system.",
    pdfUrl: lessonPDFs.lesson1,
  },
  {
    id: 2,
    number: 2,
    title: "Whole Numbers",
    description:
      "Properties of whole numbers, patterns, number line, and operations.",
    pdfUrl: lessonPDFs.lesson2,
  },
  {
    id: 3,
    number: 3,
    title: "Playing with Numbers",
    description:
      "Factors, multiples, divisibility rules, prime and composite numbers, HCF and LCM.",
    pdfUrl: lessonPDFs.lesson3,
  },
  {
    id: 4,
    number: 4,
    title: "Integers",
    description:
      "Introduction to integers, comparison, addition, and subtraction on number line.",
    pdfUrl: lessonPDFs.lesson4,
  },
  {
    id: 5,
    number: 5,
    title: "Fractions",
    description:
      "Types of fractions, equivalent fractions, comparison, addition, and subtraction.",
    pdfUrl: lessonPDFs.lesson5,
  },
  {
    id: 6,
    number: 6,
    title: "Decimals",
    description:
      "Understanding decimals, place value, comparison, and operations with decimals.",
    pdfUrl: lessonPDFs.lesson6,
  },
  {
    id: 7,
    number: 7,
    title: "Algebra",
    description:
      "Introduction to variables, algebraic expressions, and simple equations.",
    pdfUrl: lessonPDFs.lesson7,
  },
  {
    id: 8,
    number: 8,
    title: "Ratio and Proportion",
    description:
      "Understanding ratios, equivalent ratios, and solving proportion problems.",
    pdfUrl: lessonPDFs.lesson8,
  },
  {
    id: 9,
    number: 9,
    title: "Understanding Elementary Shapes",
    description:
      "Lines, line segments, angles, triangles, quadrilaterals, and circles.",
    pdfUrl: lessonPDFs.lesson9,
  },
  {
    id: 10,
    number: 10,
    title: "Mensuration",
    description:
      "Perimeter and area of squares, rectangles, and triangles. Introduction to solid shapes.",
    pdfUrl: lessonPDFs.lesson10,
  },
];
