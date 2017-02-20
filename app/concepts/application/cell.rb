class Application::Cell < Rails::View
  include ::Cell::Slim

  include ::Rails.application.routes.url_helpers

  include ActionView::Helpers::DateHelper
  include ActionView::Helpers::FormOptionsHelper
  include ActionView::Helpers::UrlHelper
  include ActionView::Helpers::CaptureHelper
  include ActionView::Helpers::OutputSafetyHelper
  include ActionView::Helpers::TranslationHelper
  include ActionDispatch::Http::Cache::Request
  include ActionView::RecordIdentifier
  include WillPaginate::ActionView
  include SimpleForm::ActionViewExtensions::FormHelper

  include ::Cell::Builder

  include AbstractController::Helpers

  EMPTY_PHOTO_PATH = "empty_photo.gif".freeze

  def render_each_and_join(views)
    views.inject("") { |partials, view| partials << render("partials/#{view}") }
  end

  def pagination
    will_paginate(model, renderer: BootstrapPagination::Rails)
  end

  def sort_column(column, title, direction = nil)
    concept("admin/base/sort_column/cell", column, title: title, direction: direction)
  end

  def sort_link(column, title = nil, direction = nil)
    concept("admin/base/sort_link/cell", column, title: title, direction: direction)
  end

  def component(name, options = {})
    concept("components/#{name}/cell", nil, options)
  end

  def search_filter(filter)
    concept("admin/base/search_filter/cell", filter)
  end

  def new_button(new_link, name)
    concept("admin/base/new_button/cell", nil, new_link: new_link, name: name)
  end

  def self.option(*array)
    array.each do |option|
      define_method(option) do
        options[option]
      end
    end
  end
end
