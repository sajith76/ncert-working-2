/**
 * User Settings Panel
 * Allows users to set their class level and preferred subject
 */

import React from "react";
import { Settings, User, BookOpen } from "lucide-react";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
} from "./ui/sheet";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import useUserStore from "../stores/userStore";

export default function UserSettingsPanel({ open, onClose }) {
  const { user, setClassLevel, setPreferredSubject } = useUserStore();

  const classLevels = [5, 6, 7, 8, 9, 10];
  const subjects = [
    "Social Science",
    "Science",
    "Mathematics",
    "English",
    "Hindi",
  ];

  const languageDescriptions = {
    5: "Very simple language (Like talking to a 10-year-old)",
    6: "Simple, clear language (Like talking to a 11-year-old)",
    7: "Clear language with some details (Like talking to a 12-year-old)",
    8: "Standard language with technical terms explained (Like talking to a 13-year-old)",
    9: "Academic language with technical terms (Like talking to a 14-year-old)",
    10: "Full academic language (Board exam preparation level)",
  };

  return (
    <Sheet open={open} onOpenChange={onClose}>
      <SheetContent side="right" className="w-[400px] max-w-[90vw]">
        <SheetHeader className="mb-6">
          <SheetTitle className="flex items-center gap-2">
            <Settings className="h-5 w-5" />
            User Settings
          </SheetTitle>
          <SheetDescription>
            Customize your learning experience
          </SheetDescription>
        </SheetHeader>

        <div className="space-y-6">
          {/* Class Level Selection */}
          <div>
            <div className="flex items-center gap-2 mb-3">
              <User className="h-4 w-4 text-muted-foreground" />
              <p className="text-sm font-medium">Your Class Level</p>
            </div>
            <div className="grid grid-cols-3 gap-2">
              {classLevels.map((level) => (
                <Button
                  key={level}
                  variant={user.classLevel === level ? "default" : "outline"}
                  className="h-auto py-3"
                  onClick={() => setClassLevel(level)}
                >
                  <div className="text-center">
                    <div className="text-lg font-bold">Class {level}</div>
                  </div>
                </Button>
              ))}
            </div>
            
            {/* Language Description */}
            <div className="mt-3 p-3 rounded-lg bg-muted/30">
              <p className="text-xs text-muted-foreground">
                <strong>AI Language Level:</strong>
              </p>
              <p className="text-sm mt-1">
                {languageDescriptions[user.classLevel]}
              </p>
            </div>
          </div>

          {/* Subject Selection */}
          <div>
            <div className="flex items-center gap-2 mb-3">
              <BookOpen className="h-4 w-4 text-muted-foreground" />
              <p className="text-sm font-medium">Preferred Subject</p>
            </div>
            <div className="flex flex-wrap gap-2">
              {subjects.map((subject) => (
                <Button
                  key={subject}
                  variant={
                    user.preferredSubject === subject ? "default" : "outline"
                  }
                  size="sm"
                  onClick={() => setPreferredSubject(subject)}
                >
                  {subject}
                </Button>
              ))}
            </div>
          </div>

          {/* Current Settings Summary */}
          <div className="mt-6 p-4 rounded-lg border bg-card">
            <p className="text-sm font-medium mb-3">Current Settings</p>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Class:</span>
                <Badge>Class {user.classLevel}</Badge>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Subject:</span>
                <Badge variant="secondary">{user.preferredSubject}</Badge>
              </div>
            </div>
          </div>

          {/* Info Box */}
          <div className="p-3 rounded-lg bg-blue-50 dark:bg-blue-950/20 border border-blue-200 dark:border-blue-800">
            <p className="text-xs text-blue-900 dark:text-blue-100">
              <strong>Tip:</strong> The AI will adjust its language complexity based on your class level. 
              Class 5 gets very simple explanations, while Class 10 gets more detailed, academic language.
            </p>
          </div>

          <Button className="w-full" onClick={onClose}>
            Save Settings
          </Button>
        </div>
      </SheetContent>
    </Sheet>
  );
}
