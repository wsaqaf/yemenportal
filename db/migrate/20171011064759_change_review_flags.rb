class ChangeReviewFlags < ActiveRecord::Migration[5.0]
  def up
    FlagsMigration.new(from: old_flags, to: new_flags).migrate
  end

  def down
    FlagsMigration.new(from: new_flags, to: old_flags).migrate
  end

  private

  class FlagsMigration
    class Flag < ApplicationRecord; end
    class Review < ApplicationRecord; end

    def initialize(from:, to:)
      @source_flags_attrs = from
      @destination_flags_attrs = to
    end

    def migrate
      update_source_with_destination
      update_reviews_with_removing_destination
      remove_useless_destination
    end

    private

    def update_source_with_destination
      @destination_flags_attrs.each do |destination_flag_tag, destination_flag_attrs|
        source_flag_attrs = @source_flags_attrs.delete(destination_flag_tag)
        if source_flag_attrs.present?
          Flag.where(source_flag_attrs).update_all(destination_flag_attrs)
        else
          Flag.create(destination_flag_attrs)
        end
      end
    end

    def update_reviews_with_removing_destination
      Review
        .where(flag_id: source_flags_to_remove.select(:id))
        .update_all(flag_id: destination_other_flag_id)
    end

    def remove_useless_destination
      source_flags_to_remove.destroy_all
    end

    def source_flags_to_remove
      Flag.where(name: source_tags_names)
    end

    def source_tags_names
      @source_flags_attrs.values.map { |t| t[:name] }
    end

    def destination_other_flag_id
      Flag.where(name: @destination_flags_attrs.dig(:other, :name)).select(:id)
    end
  end

  def new_flags
    {
      passed: { name: "تمت المراجعة", color: "#95da85" },
      copied: { name: "منقول", color: "#ff2323" },
      deceitful: { name: "مضلل", color: "#5575d5" },
      missing_reference: { name: "بلا مرجع", color: "#795548" },
      other: { name: "ملاحظة أخرى", color: "#e67e22" }
    }
  end

  def old_flags
    {
      passed: { name: "مناسب", color: "#95da85" },
      deceitful: { name: "كاذب", color: "#252025" },
      exaggerated: { name: "عنوان مبالغ فيه", color: "#5575d5" },
      inappropriate_photos: { name: "صور غير ملائمة", color: "#efc632" },
      inappropriate_content: { name: "محتوى غير ملائم", color: "#dd70ff" },
      advertising: { name: "دعايةاو اعلان", color: "#ff2323" },
      other: { name: "غير ذلك", color: "#adadad" },
      copied: { name: "منقول", color: "#edde17" }
    }
  end
end
