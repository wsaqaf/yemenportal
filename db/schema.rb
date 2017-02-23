# This file is auto-generated from the current state of the database. Instead
# of editing this file, please use the migrations feature of Active Record to
# incrementally modify your database, and then regenerate this schema definition.
#
# Note that this schema.rb definition is the authoritative source for your
# database schema. If you need to create the application database on another
# system, you should be using db:schema:load, not running all the migrations
# from scratch. The latter is a flawed and unsustainable approach (the more migrations
# you'll amass, the slower it'll run and the greater likelihood for issues).
#
# It's strongly recommended that you check this file into your version control system.

ActiveRecord::Schema.define(version: 20170222142555) do

  # These are extensions that must be enabled in order to support this database
  enable_extension "plpgsql"

  create_table "categories", force: :cascade do |t|
    t.string   "name",       null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
  end

  create_table "post_categories", force: :cascade do |t|
    t.integer  "post_id",     null: false
    t.integer  "category_id", null: false
    t.datetime "created_at",  null: false
    t.datetime "updated_at",  null: false
    t.index ["category_id"], name: "index_post_categories_on_category_id", using: :btree
    t.index ["post_id"], name: "index_post_categories_on_post_id", using: :btree
  end

  create_table "posts", force: :cascade do |t|
    t.text     "description"
    t.datetime "published_at", null: false
    t.string   "link",         null: false
    t.string   "title",        null: false
    t.datetime "created_at",   null: false
    t.datetime "updated_at",   null: false
    t.integer  "source_id"
    t.index ["published_at"], name: "index_posts_on_published_at", using: :btree
    t.index ["source_id"], name: "index_posts_on_source_id", using: :btree
  end

  create_table "sources", force: :cascade do |t|
    t.string   "link",       null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
  end

  add_foreign_key "post_categories", "categories", on_delete: :cascade
  add_foreign_key "post_categories", "posts", on_delete: :cascade
end
