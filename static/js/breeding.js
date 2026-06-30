const modal = document.getElementById("matingModal");
    const detailModal = document.getElementById("matingDetailModal");
    const facilityFilter = document.getElementById("facility_id");
    const roomFilter = document.getElementById("room_filter");

    function updateRoomOptionsForFacility() {
      const selectedFacility = facilityFilter.value;
      Array.from(roomFilter.options).forEach((option) => {
        if (option.value === "all") {
          option.hidden = false;
          return;
        }

        option.hidden =
          selectedFacility !== "all" &&
          option.dataset.facilityId !== selectedFacility;
      });

      const selectedRoomOption = roomFilter.selectedOptions[0];
      if (selectedRoomOption && selectedRoomOption.hidden) {
        roomFilter.value = "all";
      }
    }

    facilityFilter.addEventListener("change", updateRoomOptionsForFacility);
    updateRoomOptionsForFacility();

    document.querySelectorAll("[data-open-modal]").forEach((button) => {
      button.addEventListener("click", () => {
        modal.classList.add("is-open");
        modal.setAttribute("aria-hidden", "false");
      });
    });

    document.querySelectorAll("[data-start-mating]").forEach((button) => {
      button.addEventListener("click", () => {
        document.getElementById("room_id").value = button.dataset.roomId;
        document.getElementById("principal_investigator").value = button.dataset.pi;
        document.getElementById("strain").value = button.dataset.strain;
        document.getElementById("mating_type").value = "Pair: 1 male + 1 female";
        document.getElementById("sire_id").value = "";
        document.getElementById("male_source_cage_id").value = "";
        document.getElementById("dam_id").value = button.dataset.femaleId;
        document.getElementById("dam2_id").value = "";
        document.getElementById("cage_id").value = button.dataset.cageId;
        document.getElementById("status").value = "Active";
        modal.classList.add("is-open");
        modal.setAttribute("aria-hidden", "false");
      });
    });

    document.querySelectorAll("[data-use-male]").forEach((button) => {
      button.addEventListener("click", () => {
        document.getElementById("room_id").value = button.dataset.roomId;
        document.getElementById("principal_investigator").value = button.dataset.pi;
        document.getElementById("strain").value = button.dataset.strain;
        document.getElementById("sire_id").value = button.dataset.maleId;
        document.getElementById("male_source_cage_id").value = button.dataset.sourceCageId;
        document.getElementById("status").value = "Active";
        modal.classList.add("is-open");
        modal.setAttribute("aria-hidden", "false");
      });
    });

    document.querySelectorAll("[data-close-modal]").forEach((button) => {
      button.addEventListener("click", () => {
        modal.classList.remove("is-open");
        modal.setAttribute("aria-hidden", "true");
      });
    });

    modal.addEventListener("click", (event) => {
      if (event.target === modal) {
        modal.classList.remove("is-open");
        modal.setAttribute("aria-hidden", "true");
      }
    });

    const detailFields = {
      pairId: document.getElementById("detailPairId"),
      status: document.getElementById("detailStatus"),
      facility: document.getElementById("detailFacility"),
      room: document.getElementById("detailRoom"),
      pi: document.getElementById("detailPi"),
      strain: document.getElementById("detailStrain"),
      setup: document.getElementById("detailSetup"),
      cage: document.getElementById("detailCage"),
      sire: document.getElementById("detailSire"),
      dams: document.getElementById("detailDams"),
      startDate: document.getElementById("detailStartDate"),
      plan: document.getElementById("detailPlan"),
      visualSire: document.getElementById("detailVisualSire"),
      visualDams: document.getElementById("detailVisualDams"),
      pedigreeSireId: document.getElementById("pedigreeSireId"),
      pedigreeDamId: document.getElementById("pedigreeDamId"),
      litterPairId: document.getElementById("detailLitterPairId"),
      litterRoomId: document.getElementById("detailLitterRoomId"),
      litterId: document.getElementById("detailLitterId"),
      maleCagePairId: document.getElementById("detailMaleCagePairId"),
      maleCageRoomId: document.getElementById("detailMaleCageRoomId"),
      maleMouseId: document.getElementById("detailMaleMouseId"),
      maleCageId: document.getElementById("detailMaleCageId"),
      weanPairId: document.getElementById("detailWeanPairId"),
      weanRoomId: document.getElementById("detailWeanRoomId"),
      femaleWeanCage: document.getElementById("detailFemaleWeanCage"),
      maleWeanCage: document.getElementById("detailMaleWeanCage"),
      deliveryCount: document.getElementById("detailDeliveryCount"),
      damAgeMonths: document.getElementById("detailDamAgeMonths"),
      retireSignal: document.getElementById("detailRetireSignal"),
      hidePairId: document.getElementById("detailHidePairId"),
      hideRoomId: document.getElementById("detailHideRoomId"),
      hideButton: document.getElementById("detailHideButton"),
      hiddenNote: document.getElementById("detailHiddenNote"),
      printCardLink: document.getElementById("detailPrintCardLink"),
    };

    function updateRetirementSignal() {
      const deliveries = Number(detailFields.deliveryCount.textContent || 0);
      const ageMonths = Number(detailFields.damAgeMonths.value || 0);
      const shouldRetire = deliveries >= 4 || ageMonths >= 8;

      detailFields.retireSignal.textContent = shouldRetire ? "Retire female" : "Continue breeding";
      detailFields.retireSignal.parentElement.classList.toggle("is-warning", shouldRetire);
    }

    document.querySelectorAll("[data-detail-button]").forEach((button) => {
      button.addEventListener("click", () => {
        detailFields.pairId.textContent = button.dataset.pairId;
        detailFields.status.textContent = button.dataset.status;
        detailFields.facility.textContent = button.dataset.facility;
        detailFields.room.textContent = button.dataset.room;
        detailFields.pi.textContent = button.dataset.pi;
        detailFields.strain.textContent = button.dataset.strain;
        detailFields.setup.textContent = button.dataset.setup;
        detailFields.cage.textContent = button.dataset.cage;
        detailFields.sire.textContent = button.dataset.sire;
        detailFields.dams.textContent = button.dataset.dams;
        detailFields.startDate.textContent = button.dataset.startDate;
        detailFields.plan.textContent = button.dataset.plan;
        detailFields.visualSire.textContent = button.dataset.sire;
        detailFields.visualDams.textContent = button.dataset.dams;
        detailFields.pedigreeSireId.textContent = button.dataset.sire;
        detailFields.pedigreeDamId.textContent = button.dataset.dams;
        detailFields.litterPairId.value = button.dataset.pairId;
        detailFields.litterRoomId.value = button.dataset.roomId;
        detailFields.maleCagePairId.value = button.dataset.pairId;
        detailFields.maleCageRoomId.value = button.dataset.roomId;
        detailFields.weanPairId.value = button.dataset.pairId;
        detailFields.weanRoomId.value = button.dataset.roomId;
        detailFields.hidePairId.value = button.dataset.pairId;
        detailFields.hideRoomId.value = button.dataset.roomId;
        detailFields.litterId.placeholder = `L-${button.dataset.pairId.replace("BP-", "")}`;
        detailFields.maleMouseId.value = button.dataset.sire;
        detailFields.maleCageId.placeholder = `CAGE-M-${button.dataset.pairId.replace("BP-", "")}`;
        detailFields.femaleWeanCage.placeholder = `CAGE-FW-${button.dataset.pairId.replace("BP-", "")}`;
        detailFields.maleWeanCage.placeholder = `CAGE-MW-${button.dataset.pairId.replace("BP-", "")}`;
        detailFields.deliveryCount.textContent = button.dataset.litterCount || "0";
        detailFields.damAgeMonths.value = "";
        const isHidden = button.dataset.hidden === "1";
        detailFields.hideButton.disabled = isHidden;
        detailFields.hideButton.textContent = isHidden ? "Already hidden" : "Hide retired mating";
        detailFields.hiddenNote.textContent = isHidden
          ? "This mating is hidden from the active list, but its data is still saved."
          : "This hides the mating from the active list but keeps all data.";
        detailFields.printCardLink.href = `/breeding/${encodeURIComponent(button.dataset.pairId)}/card`;
        updateRetirementSignal();
        document.getElementById("matingDetailTitle").textContent = `${button.dataset.pairId} Details`;
        detailModal.classList.add("is-open");
        detailModal.setAttribute("aria-hidden", "false");
      });
    });

    detailFields.damAgeMonths.addEventListener("input", updateRetirementSignal);

    const breedingRows = Array.from(document.querySelectorAll("[data-breeding-row]"));
    const breedingFilterNote = document.getElementById("breedingFilterNote");
    const breedingFilterText = document.getElementById("breedingFilterText");
    const breedingMatingsPanel = document.getElementById("breedingMatingsPanel");

    document.querySelectorAll("[data-summary-filter]").forEach((button) => {
      button.addEventListener("click", () => {
        const room = button.dataset.summaryRoom;
        const pi = button.dataset.summaryPi;
        const strain = button.dataset.summaryStrain;

        breedingRows.forEach((row) => {
          const matches =
            row.dataset.rowRoom === room &&
            row.dataset.rowPi === pi &&
            row.dataset.rowStrain === strain;
          row.hidden = !matches;
        });

        breedingFilterText.textContent = `Showing breeding records for ${pi} / ${strain} in ${room}.`;
        breedingFilterNote.hidden = false;
        breedingMatingsPanel.scrollIntoView({ behavior: "smooth", block: "start" });
      });
    });

    document.getElementById("clearBreedingFilter").addEventListener("click", () => {
      breedingRows.forEach((row) => {
        row.hidden = false;
      });
      breedingFilterNote.hidden = true;
    });

    document.querySelectorAll("[data-detail-close]").forEach((button) => {
      button.addEventListener("click", () => {
        detailModal.classList.remove("is-open");
        detailModal.setAttribute("aria-hidden", "true");
      });
    });

    detailModal.addEventListener("click", (event) => {
      if (event.target === detailModal) {
        detailModal.classList.remove("is-open");
        detailModal.setAttribute("aria-hidden", "true");
      }
    });