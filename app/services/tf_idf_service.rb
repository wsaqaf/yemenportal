require "matrix"

class TfIdfService
  attr_reader :description, :config

  def initialize(description:)
    @description = description
    @config = Rails.application.config_for(:tf_idf_settings)
  end

  def post_topic
    model = TfIdfSimilarity::TfIdfModel.new([current_model] + tf_idf_posts.values)
    matrix = model.similarity_matrix

    post_data = main_post(model, matrix)
    find_topic(post_data[:id]) if post_data[:id]
  end

  private

  def main_post(model, matrix)
    current_index = model.document_index(current_model)
    tf_idf_posts.inject({}) do |result, (id, post)|
      percent = matrix[current_index, model.document_index(post)]
      result = { id: id, percent: percent } if percent > config["min_percent"] && percent > (result[:percent] || 0)
      result
    end
  end

  def find_topic(id)
    post = posts.find { |element| element.id == id }
    topic = post.topic
    topic ? topic : Topic.create(posts: [post])
  end

  def tf_idf_posts
    @_tf_idf_posts ||= posts.reduce({}) do |result, post|
      result.merge(post.id => TfIdfSimilarity::Document.new(post.stemmed_text))
    end
  end

  def posts
    @_posts = Post.where(created_at: config["hours_period"].hours.ago..Time.current)
  end

  def current_model
    @_current ||= TfIdfSimilarity::Document.new(description)
  end
end
