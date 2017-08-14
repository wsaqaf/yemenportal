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
  include Pundit
  include Devise::Controllers::Helpers

  include ::Cell::Builder

  include AbstractController::Helpers

  def self.option(*array)
    array.each do |option|
      define_method(option) do
        options[option]
      end
    end
  end

  def render_each_and_join(views)
    views.inject("") { |partials, view| partials << render("partials/#{view}") }
  end

  def pagination
    will_paginate(model, renderer: FoundationPagination::Rails)
  end

  def url_for(options)
    parent_controller.url_for(options)
  end

  def scoped_translation(key, params = {})
    scope = self.class.name.sub(/::Cell$/, "").underscore.tr("/", ".")
    I18n.t("#{scope}.#{key}", params)
  end

  alias st scoped_translation
end
