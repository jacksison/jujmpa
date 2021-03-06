<template>

  <div>

    <div class="d-lg-flex justify-content-lg-between mb-3">

      <div class="btn-group mb-md-0 mb-3">
        <button v-for="(optionState, optionKey) in this.filterByPresence" type="button"
                :class="['btn btn-outline-primary', optionState ? 'active' : '']"
                @click="setListContext('filterByPresence', optionKey, !optionState)">
          {{ stats[optionKey] }} {{ optionKey }}
        </button>
      </div>

      <div class="btn-group mb-md-0 mb-3" v-if="!isForVenues">
        <button v-for="(optionState, optionKey) in this.filterByType" type="button"
                :class="['btn btn-outline-primary', optionState ? 'active' : '']"
                @click="setListContext('filterByType', optionKey, !optionState)">
          {{ optionKey }}
        </button>
      </div>

      <div class="btn-group mb-md-0 mb-3" v-if="!isForVenues">
        <button v-for="(optionState, optionKey) in this.speakerGroupings" type="button"
                :class="['btn btn-outline-primary', optionState ? 'active' : '']"
                @click="setListContext('speakerGroupings', optionKey, !optionState)">
          {{ optionKey }}
        </button>
      </div>

      <div class="btn-group mb-md-0 mb-3">
        <button v-for="(optionState, optionKey) in this.sortByGroup" type="button"
                :class="['btn btn-outline-primary', optionState ? 'active' : '']"
                @click="setListContext('sortByGroup', optionKey, !optionState)">
          {{ optionKey }}
        </button>
      </div>

    </div>

    <div class="alert alert-info" v-if="entitiesByPresence.length === 0">
      No matching <span v-if="isForVenues">venues</span><span v-else>people</span> found.
    </div>
    <div class="alert alert-info">
      This page will live-update with new check-ins as they occur although the initial list may be up to a minute old. <template v-if="assistantUrl"> If you want to view this page without the sidebar (i.e. for displaying to an auditorium) you can <a :href="assistantUrl" target="_blank"> open the assistant version.</a></template>
    </div>

    <transition-group :name="mainTransitions" tag="div">
      <div v-for="(entity, grouper) in entitiesBySortingSetting"
           :key="grouper" class="card mt-1">

        <div class="card-body p-0">
          <div class="row no-gutters">

            <div class="col-12 col-md-3 col-lg-2 d-flex flex-nowrap align-items-center">

              <div class="mr-auto strong my-1 px-2">
                {{ grouper }}
              </div>
              <button v-if="scanUrl" class="btn btn-info my-1 mr-1 px-2 align-self-stretch btn-sm hoverable p-1"
                      @click="checkInGroup(entity)">
                <strong>✓</strong> All
              </button>

            </div>

            <div class="col-12 col-md-9 col-lg-10 pt-md-1 pl-md-0 pl-1">
              <transition-group :name="mainTransitions" tag="div" class="row no-gutters">


                <div v-for="entity in entity" :key="entity.id"
                     class="col-lg-3 col-md-4 col-6 check-in-person">
                  <div class="row no-gutters h6 mb-0 pb-1 pr-1 p-0 text-white">

                    <div :class="['col p-2 text-truncate ',
                                  entity.status ? 'bg-success' : 'bg-secondary',
                                  entity.type === 'Adjudicator' ? 'text-capitalize' : 'text-uppercase']"
                         data-toggle="tooltip" :title="getToolTipForEntity(entity)">
                      {{ entity.name }}
                    </div>
                    <a v-if="scanUrl && !entity.status && entity.identifier[0] && !entity.locked"
                       class="col-auto p-2 btn-info text-center hoverable"
                       title="Click to check-in manually"
                       @click="checkInIdentifiers(entity.identifier, true)">
                      ✓
                    </a>
                    <div v-if="scanUrl && !entity.status && entity.identifier[0] && entity.locked"
                         class="col-auto p-2 btn-secondary text-center btn-no-hover">
                      saving...
                    </div>
                    <div v-if="scanUrl && !entity.identifier[0]"
                         class="col-auto p-2 btn-secondary text-white text-center"
                         data-toggle="tooltip" title="This person does not have a check-in identifier so can't be checked in">
                      ?
                    </div>
                    <div v-if="entity.status" title="Click to undo a check-in"
                         class="col-auto p-2 btn-success hoverable text-center"
                         @click="checkInIdentifiers(entity.identifier, false)">
                      {{ lastSeenTime(entity.status.time) }}
                    </div>

                  </div>
                </div>

              </transition-group>
            </div>

          </div>
        </div>

      </div>
    </transition-group>

  </div>

</template>

<script>
import _ from 'lodash'

import AjaxMixin from '../../templates/ajax/AjaxMixin.vue'
import WebSocketMixin from '../../templates/ajax/WebSocketMixin.vue'
import PeopleStatusMixin from './PeopleStatusMixin.vue'
import VenuesStatusMixin from './VenuesStatusMixin.vue'

export default {
  mixins: [AjaxMixin, WebSocketMixin, PeopleStatusMixin, VenuesStatusMixin],
  data: function () {
    return {
      filterByPresence: {
        All: false, Absent: true, Present: false,
      },
      enableAnimations: true,
      sockets: ['checkins'],
      // Keep internal copy as events needs to be mutated by the websocket
      // pushed changes and the data is never updated by the parent
      events: this.initialEvents,
    }
  },
  props: {
    initialEvents: Array,
    scanUrl: String,
    assistantUrl: String,
    teamCodes: Boolean,
  },
  computed: {
    statsAbsent: function () {
      return 0
    },
    statsPresent: function () {
      return 0
    },
    stats: function () {
      return {
        Absent: _.filter(this.entitiesByType, (p) => {
          return p.status === false
        }).length,
        Present: _.filter(this.entitiesByType, (p) => {
          return p.status !== false
        }).length,
        All: '',
      }
    },
    isForVenues: function () {
      return this.venues === null ? false : true
    },
    filterByType: function () {
      return this.isForVenues ? this.venuesFilterByType : this.peopleFilterByType
    },
    sortByGroup: function () {
      return this.isForVenues ? this.venuesSortByGroup : this.peopleSortByGroup
    },
    mainTransitions: function () {
      // Don't want the entire list to animate when changing filter effects
      if (this.enableAnimations) {
        return 'animated-list'
      }
      return ''
    },
    entitiesByType: function () {
      return this.isForVenues ? this.venuesByType : this.peopleByType
    },
    entitiesByPresence: function () {
      // Filter by status
      if (this.filterByPresence.All) {
        return this.entitiesByType
      } else if (this.filterByPresence.Absent) {
        return _.filter(this.entitiesByType, (p) => {
          return p.status === false
        })
      }
      return _.filter(this.entitiesByType, (p) => {
        return p.status !== false
      })
    },
    entitiesSortedByName: function () {
      return _.sortBy(this.entitiesByPresence, ['name'])
    },
    entitiesByName: function () {
      return _.groupBy(this.entitiesSortedByName, (p) => {
        return p.name[0]
      })
    },
    entitiesByTime: function () {
      var sortedByTime = _.sortBy(this.entitiesSortedByName, (p) => {
        if (_.isUndefined(p.status)) {
          return 'Thu, 01 Jan 2070 00:00:00 GMT-0400'
        }
        return p.status.time
      })
      return _.groupBy(sortedByTime, (p) => {
        var time = new Date(Date.parse(p.status.time))
        var hours = this.clock(time.getHours())
        if (_.isUndefined(p.status) || p.status === false) {
          return 'Not Checked In'
        }
        if (time.getMinutes() < 30) {
          return `${hours}:00 - ${hours}:29`
        }
        return `${hours}:30 - ${hours}:59`
      })
    },
    entitiesBySortingSetting: function () {
      if (this.sortByGroup['By Category'] === true) {
        return this.venuesByCategory
      } else if (this.sortByGroup['By Priority'] === true) {
        return this.venuesByPriority
      } else if (this.sortByGroup['By Name'] === true) {
        return this.entitiesByName
      } else if (this.sortByGroup['By Institution'] === true) {
        return this.peopleByInstitution
      } else if (this.sortByGroup['By Time'] === true) {
        return this.entitiesByTime
      }
      return this.entitiesByTime
    },
  },
  methods: {
    clock: function (timeRead) {
      var paddedTime = (`0${timeRead}`).slice(-2)
      return paddedTime
    },
    checkInGroup: function (entity) {
      var identifiersForEntities = _.flatten(_.map(entity, 'identifier'))
      var nonNullIdentifiers = _.filter(identifiersForEntities, (id) => {
        return id !== null
      });
      if (nonNullIdentifiers.length > 0) {
        this.checkInIdentifiers(nonNullIdentifiers, true)
      }
    },
    checkInIdentifiers: function (barcodeIdentifiers, setStatus) {
      var message = `the checkin status of ${barcodeIdentifiers} to ${setStatus}`
      var type = this.isForVenues ? 'venues' : 'people'
      var payload = { barcodes: barcodeIdentifiers, status: setStatus, type: type }
      this.setLocked(barcodeIdentifiers, true)
      this.ajaxSave(this.scanUrl, payload, message, this.passCheckIn, this.failCheckIn, null, false)
    },
    setLocked: function (identifiers, status) {
      _.forEach(this.entitiesByType, (entity) => {
        if (_.includes(identifiers, entity.identifier)) {
          entity.locked = true
        }
      })
    },
    passCheckIn: function (dataResponse, payload, returnPayload) {
      this.setLocked(payload.barcodes, false)
    },
    failCheckIn: function (payload, returnPayload) {
      var message = `Failed to check in one or more identifiers: ${payload.barcodes}`
      $.fn.showAlert('danger', message, 0)
      this.setLocked(payload.barcodes, false)
    },
    lastSeenTime: function (timeString) {
      var time = new Date(Date.parse(timeString))
      return `${this.clock(time.getHours())}:${this.clock(time.getMinutes())}`
    },
    getToolTipForEntity: function (entity) {
      return this.isForVenues ? this.getToolTipForVenue(entity) : this.getToolTipForPerson(entity)
    },
    setListContext: function (metaKey, selectedKey, selectedValue) {
      this.enableAnimations = false
      _.forEach(this[metaKey], (value, key) => {
        if (key === selectedKey) {
          this[metaKey][key] = selectedValue
        } else {
          this[metaKey][key] = false
        }
      })
      this.$nextTick(() => {
        this.enableAnimations = true
      })
    },
    handleSocketMessage: function (payload) {
      if (payload.created === true) {
        this.events.push(payload)
      } else {
        // Revoked checkins; remove all items that match the payload identifier
        this.events = _.filter(this.events, function (event) {
          return event.identifier !== payload.identifier
        })
      }
    },
  },
}
</script>
