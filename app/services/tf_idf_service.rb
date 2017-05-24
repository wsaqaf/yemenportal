require "matrix"

class TfIdfService
  attr_reader :description, :config

  def initialize(description:)
    @description = description
    @config = Rails.application.config_for(:tf_idf_settings)
  end

  def dependent_post_ids
    model = TfIdfSimilarity::TfIdfModel.new([current_model] + tf_idf_posts.values)
    matrix = model.similarity_matrix

    current_index = model.document_index(current_model)
    tf_idf_posts.each_with_object([]) do |(id, post), result|
      result << id if matrix[current_index, model.document_index(post)] > config["matrix_border"]
    end
  end

  private

  def tf_idf_posts
    @_posts ||= Post.where(created_at: config["hours_period"].hours.ago..Time.current).reduce({}) do |result, post|
      result.merge(post.id => TfIdfSimilarity::Document.new(ActionView::Base.full_sanitizer.sanitize(post.description)))
    end
  end

  def current_model
    @_current ||= TfIdfSimilarity::Document.new(ActionView::Base.full_sanitizer.sanitize(description))
  end
end
