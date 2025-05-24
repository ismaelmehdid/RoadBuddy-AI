import { CallbackAnswer, City, Countries } from "../types/types";

export function interpretCallback(
      callback: string,
    ): CallbackAnswer {
      switch (callback) {
        case "FRANCE":
          return CallbackAnswer.FRANCE;
        case "PARIS":
          return CallbackAnswer.PARIS;
        case "A":
          return CallbackAnswer.A;
        case "B":
          return CallbackAnswer.B;
        case "C":
          return CallbackAnswer.C;
        case "D":
          return CallbackAnswer.D;
        default:
          console.error(`Unknown callback: ${callback}`);
          return CallbackAnswer.ERROR;
    }
}

export function interpretCountry(
      country: CallbackAnswer,
    ): Countries | null {
      switch (country) {
        case CallbackAnswer.FRANCE:
          return Countries.FRANCE;
        default:
          return null;
    }
}

export function interpretCity(
      city: CallbackAnswer,
    ): City | null {
      switch (city) {
        case CallbackAnswer.PARIS:
          return City.PARIS;
        default:
          return null;
    }
}