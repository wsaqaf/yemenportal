require "matrix"

class TfIdfService
  attr_reader :stemmed_text, :config

  def initialize(stemmed_text:)
    @stemmed_text = stemmed_text
    @config = Rails.application.config_for(:tf_idf_settings)
  end

  def post_topic
    model = TfIdfSimilarity::TfIdfModel.new([current_model] + tf_idf_posts.values)
    matrix = model.similarity_matrix

    post_data_id = main_post(model, matrix)
    find_topic(post_data_id) if post_data_id
  end

  private

  def main_post(model, matrix)
    similar_model = max_similaty(model, matrix)

    if similar_model && similar_model[:value] > @config["min_percent"]
      greater_model = model.documents[similar_model[:id]]
      tf_idf_posts.detect { |(_id, post_model)| post_model == greater_model }[0]
    end
  end

  def max_similaty(model, matrix)
    current_index = model.document_index(current_model)

    row = matrix.row(current_index)
    if row.count > 1
      result = row.each_with_index.reject { |(_value, index)| index == current_index }.max { |(value, _index)| value }
      { value: result[0], id: result[1] }
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
    @_current ||= TfIdfSimilarity::Document.new(stemmed_text)
  end
end
